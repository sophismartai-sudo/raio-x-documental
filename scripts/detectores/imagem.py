# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
import os
import shutil
import subprocess
import tempfile
from typing import List, Optional, Tuple

from PIL import Image, ImageOps

from achados import Achado, SEV_MEDIO
from severidade import para
from padroes_injecao import casar_injecao
from normalizacao import normalizar
from contraste import faixa_luminancia

CONTRASTE_MIN = 24.0
LANGS_PREF = ("por", "eng")
CONF_MIN = 30.0
MIN_ALNUM = 3
TECNICA_OCULTA = "baixo_contraste"
TECNICA_VISIVEL = "texto_visivel"

# Altura (px) das faixas horizontais usadas no realce de contraste local — ver
# `_autocontraste_por_faixas`. Default calibrado empiricamente (não uma medição
# formal): grande o bastante para caber a linha oculta, pequeno o bastante para
# isolá-la de texto normal em outra parte da mesma imagem.
FAIXA_REALCE_PX = 100

_TIMEOUT_OCR = 120

# Candidatos usados quando "tesseract" não está no PATH — comum em máquinas
# Windows de usuários não técnicos, onde o instalador não adiciona o binário
# ao PATH automaticamente. Construído a partir de variáveis de ambiente
# (puladas quando ausentes) + caminhos fixos comuns em macOS/Linux.
_CAMINHOS_TESSERACT_POR_ENV = (
    ("ProgramFiles", ("Tesseract-OCR", "tesseract.exe")),
    ("ProgramFiles(x86)", ("Tesseract-OCR", "tesseract.exe")),
    ("LOCALAPPDATA", ("Programs", "Tesseract-OCR", "tesseract.exe")),
    ("LOCALAPPDATA", ("Tesseract-OCR", "tesseract.exe")),
)
_CAMINHOS_TESSERACT_FIXOS = (
    "/opt/homebrew/bin/tesseract",
    "/usr/local/bin/tesseract",
    "/usr/bin/tesseract",
)


def _tesseract() -> Optional[str]:
    encontrado = shutil.which("tesseract")
    if encontrado:
        return encontrado
    candidatos = []
    for variavel, partes in _CAMINHOS_TESSERACT_POR_ENV:
        base = os.environ.get(variavel)
        if base:
            candidatos.append(os.path.join(base, *partes))
    candidatos.extend(_CAMINHOS_TESSERACT_FIXOS)
    for caminho in candidatos:
        if os.path.isfile(caminho):
            return caminho
    return None


def _langs(binp: str) -> str:
    try:
        out = subprocess.run([binp, "--list-langs"], capture_output=True,
                             text=True, timeout=30)
        disp = set(out.stdout.split())
    except Exception:
        disp = set()
    sel = [l for l in LANGS_PREF if l in disp]
    return "+".join(sel) if sel else "eng"


def _autocontraste_por_faixas(cinza: "Image.Image", altura: int = FAIXA_REALCE_PX) -> "Image.Image":
    """Autocontraste aplicado por faixa horizontal, não na imagem inteira.

    Necessário porque `ImageOps.autocontrast` na imagem inteira é um no-op quando
    já existe texto de alto contraste (preto/branco) em outra parte da MESMA
    imagem: o mínimo e o máximo globais já cobrem 0-255, então não há nada para
    esticar, e a linha oculta (ex.: cinza-claro sobre branco) nunca ultrapassa o
    limiar que o OCR consegue enxergar — verificado empiricamente com o binário
    tesseract (uma página com uma linha preta normal + uma linha em baixíssimo
    contraste em outro ponto da página faz o texto oculto desaparecer em TODAS as
    variantes, mesmo isolado por centenas de pixels). Processar em faixas isola a
    região da linha oculta do restante da página, permitindo que o autocontraste
    local a realce."""
    W, H = cinza.size
    saida = Image.new("L", (W, H))
    for y0 in range(0, H, altura):
        y1 = min(H, y0 + altura)
        faixa = cinza.crop((0, y0, W, y1))
        saida.paste(ImageOps.autocontrast(faixa, cutoff=0), (0, y0))
    return saida


def _linhas_do_tsv(tsv: str) -> List[Tuple[str, int, int, int, int, float]]:
    """Agrupa palavras TSV por (block,par,line) -> (texto, x0,y0,x1,y1, conf_min)."""
    grupos: dict = {}
    for ln in tsv.splitlines()[1:]:
        c = ln.split("\t")
        if len(c) < 12:
            continue
        txt = c[11].strip()
        if not txt:
            continue
        try:
            conf = float(c[10])
            left, top, w, h = int(c[6]), int(c[7]), int(c[8]), int(c[9])
        except ValueError:
            continue
        if conf < CONF_MIN:
            continue
        chave = (c[2], c[3], c[4])
        g = grupos.setdefault(chave, {"p": [], "x0": 10 ** 9, "y0": 10 ** 9,
                                      "x1": 0, "y1": 0, "conf": 100.0})
        g["p"].append(txt)
        g["x0"] = min(g["x0"], left)
        g["y0"] = min(g["y0"], top)
        g["x1"] = max(g["x1"], left + w)
        g["y1"] = max(g["y1"], top + h)
        g["conf"] = min(g["conf"], conf)
    return [(" ".join(g["p"]), g["x0"], g["y0"], g["x1"], g["y1"], g["conf"])
            for g in grupos.values()]


def _ocr_tsv(binp: str, img: "Image.Image", langs: str, tmp: List[str]) -> str:
    fd, p = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    tmp.append(p)
    img.save(p)
    r = subprocess.run([binp, p, "stdout", "-l", langs, "tsv"],
                       capture_output=True, text=True, timeout=_TIMEOUT_OCR)
    return r.stdout


def analisar_imagem_pil(img: "Image.Image", local: str = "imagem") -> List[Achado]:
    binp = _tesseract()
    if not binp:
        return [Achado(tecnica="ocr_indisponivel", severidade=SEV_MEDIO, local=local,
                       trecho="OCR (tesseract) indisponível — imagem NÃO verificada; "
                              "instale o tesseract e rode novamente.",
                       evidencia={"motivo": "binário tesseract ausente no PATH"})]
    langs = _langs(binp)
    rgb = img.convert("RGB")
    cinza = ImageOps.grayscale(rgb)     # 'L' = luminância do ORIGINAL (base do contraste)
    px = cinza.load()
    W, H = cinza.size

    variantes = [rgb, _autocontraste_por_faixas(cinza), ImageOps.invert(cinza)]
    tmp: List[str] = []
    achados: List[Achado] = []
    vistos = set()
    try:
        for v in variantes:
            for (texto, x0, y0, x1, y1, conf) in _linhas_do_tsv(_ocr_tsv(binp, v, langs, tmp)):
                norm = normalizar(texto)
                chave = (norm.lower(), x0 // 10, y0 // 10)
                if chave in vistos:
                    continue
                vistos.add(chave)
                inj = casar_injecao(norm)
                faixa = faixa_luminancia(px, W, H, x0, y0, x1, y1)
                oculto = (faixa < CONTRASTE_MIN
                          and sum(ch.isalnum() for ch in texto) >= MIN_ALNUM)
                if not oculto and not inj:
                    continue
                tecnica = TECNICA_OCULTA if oculto else TECNICA_VISIVEL
                achados.append(Achado(
                    tecnica=tecnica,
                    severidade=para(tecnica, bool(inj)),
                    local=local,
                    trecho=texto,
                    decodificado=norm if norm != texto else None,
                    evidencia={"contraste": round(faixa, 1), "conf_ocr": round(conf, 1),
                               "bbox": [x0, y0, x1, y1], "categorias_injecao": inj},
                ))
    finally:
        for p in tmp:
            try:
                os.remove(p)
            except OSError:
                pass
    return achados


def analisar_imagem(caminho: str) -> List[Achado]:
    with Image.open(caminho) as img:
        img.load()
        return analisar_imagem_pil(img, local=os.path.basename(caminho))


def texto_visivel_ocr(caminho: str) -> Optional[str]:
    """OCR as-is do original (texto visível). None se tesseract ausente.

    Usado pela higienização (Fase 4) para extrair o texto integral de imagens:
    OCR sem realce de contraste só lê o que já é visível a olho nu — texto em
    baixíssimo contraste (técnica `baixo_contraste`) não aparece as-is, então
    fica de fora daqui por construção (é por isso que é considerado oculto)."""
    binp = _tesseract()
    if not binp:
        return None
    langs = _langs(binp)
    tmp: List[str] = []
    try:
        with Image.open(caminho) as img:
            img.load()
            rgb = img.convert("RGB")
        linhas = _linhas_do_tsv(_ocr_tsv(binp, rgb, langs, tmp))
        return "\n".join(t for (t, *_r) in linhas)
    finally:
        for p in tmp:
            try:
                os.remove(p)
            except OSError:
                pass
