# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
import datetime
import os
import pathlib
from typing import List, Optional, Tuple

from severidade import TECNICAS_OCULTACAO
from padroes_injecao import casar_injecao
from normalizacao import normalizar, INVISIVEIS, BIDI, TAG_INI, TAG_FIM

VERSAO = "raio-x-documental 0.1"


def _remover_contrabando(texto: str) -> str:
    """Remove (NÃO decodifica) invisíveis, BIDI e Tags Unicode. Ao contrário de
    normalizar(), que decodifica Tags para ASCII — o que reintroduziria o comando
    escondido na cópia dita 'segura'."""
    return "".join(
        ch for ch in texto
        if ord(ch) not in INVISIVEIS
        and ord(ch) not in BIDI
        and not (TAG_INI <= ord(ch) <= TAG_FIM)
    )


def _texto_integral(caminho: str, tipo: str) -> Optional[str]:
    """Todo o texto (visível + oculto) do documento, por formato. None só p/ imagem sem OCR."""
    if tipo == "txt":
        return pathlib.Path(caminho).read_text(encoding="utf-8", errors="replace")
    if tipo == "pdf":
        import fitz
        doc = fitz.open(caminho)
        try:
            return "\n".join(p.get_text("text") for p in doc)
        finally:
            doc.close()
    if tipo == "docx":
        import zipfile
        from lxml import etree
        from xml_seguro import parse_xml
        W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        linhas: List[str] = []
        with zipfile.ZipFile(caminho) as z:
            for parte in [n for n in z.namelist() if n.startswith("word/") and n.endswith(".xml")]:
                try:
                    root = parse_xml(z.read(parte))
                except etree.XMLSyntaxError:
                    continue        # parte ilegível: pulada aqui é seguro (nunca vaza, só perde texto);
                                     # o detector (analisar_docx) já registrou o achado "nao_verificado"
                for p in root.iter(f"{W}p"):
                    linhas.append("".join(t.text or "" for t in p.iter(f"{W}t")))
        return "\n".join(linhas)
    if tipo == "odt":
        import zipfile
        from lxml import etree
        from xml_seguro import parse_xml
        TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
        with zipfile.ZipFile(caminho) as z:
            try:
                root = parse_xml(z.read("content.xml"))
            except (KeyError, etree.XMLSyntaxError):
                return ""           # ausente/ilegível: o detector já registrou "nao_verificado"
        return "\n".join("".join(p.itertext()) for p in root.iter(f"{{{TEXT}}}p"))
    if tipo == "rtf":
        from detectores.rtf import _limpar_controles
        with open(caminho, "r", encoding="latin-1", errors="replace") as f:
            return _limpar_controles(f.read())
    if tipo == "html":
        from detectores.html_email import _carregar
        from lxml import html as lhtml
        conteudo = _carregar(caminho)
        return lhtml.fromstring(conteudo).text_content() if conteudo.strip() else ""
    if tipo == "imagem":
        from detectores.imagem import texto_visivel_ocr
        return texto_visivel_ocr(caminho)
    raise ValueError(f"higienização não suporta o tipo: {tipo}")


def gerar_neutralizado(caminho: str, resultado: dict) -> Tuple[Optional[str], int]:
    """(texto_neutralizado, n_linhas_removidas). texto=None se imagem sem OCR."""
    bruto = _texto_integral(caminho, resultado.get("tipo", ""))
    if bruto is None:
        return (None, 0)
    limpo = _remover_contrabando(bruto)
    alvos = []
    for a in resultado.get("achados", []):
        if a.get("tecnica") in TECNICAS_OCULTACAO:
            alvo = normalizar(a.get("trecho", "")).strip().lower()
            if alvo and not alvo.startswith("<"):   # ignora placeholders tipo "<tags unicode…>"
                alvos.append(alvo)
    mantidas: List[str] = []
    removidas = 0
    for linha in limpo.splitlines():
        norm = normalizar(linha)
        chave = norm.strip().lower()
        if chave and (any(alvo in chave for alvo in alvos) or casar_injecao(norm)):
            removidas += 1
            continue
        mantidas.append(linha)
    return ("\n".join(mantidas), removidas)


def gerar_extracao_oculta(resultado: dict) -> Tuple[str, int]:
    """(corpo, n_itens). Lista os achados relevantes (severidade != INFO), decodificados."""
    relevantes = [a for a in resultado.get("achados", []) if a.get("severidade") != "INFO"]
    if not relevantes:
        return ("Nenhum conteúdo oculto ou comando suspeito foi extraído.", 0)
    linhas: List[str] = []
    for a in relevantes:
        linhas.append(f"[{a.get('severidade','')}] {a.get('tecnica','')} @ {a.get('local','')}")
        linhas.append(f"  texto: {a.get('trecho','')}")
        dec = a.get("decodificado")
        if dec and dec != a.get("trecho"):
            linhas.append(f"  decodificado: {dec}")
        cats = (a.get("evidencia") or {}).get("categorias_injecao")
        if cats:
            linhas.append(f"  categorias de injeção: {', '.join(cats)}")
        linhas.append("")
    return ("\n".join(linhas), len(relevantes))


def _cabecalho(resultado: dict, titulo: str, extra: str = "") -> str:
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linhas = [
        "=" * 70, titulo,
        f"Documento original : {resultado.get('arquivo', '')}",
        f"SHA-256 (original) : {resultado.get('sha256', '')}",
        f"Veredito da análise: {resultado.get('veredito', '')}",
        f"Ferramenta         : {resultado.get('ferramenta_versao', VERSAO)}",
        f"Gerado em          : {agora}",
    ]
    if extra:
        linhas.append(extra)
    linhas += [
        "AVISO: arquivo DERIVADO gerado automaticamente. NÃO substitui o original,",
        "que permanece intacto. Confira sempre contra o documento de origem.",
        "=" * 70, "",
    ]
    return "\n".join(linhas)


def higienizar(caminho: str, resultado: dict, destino: str, *,
               neutralizar: bool = True, extrair_oculto: bool = True) -> List[str]:
    os.makedirs(destino, exist_ok=True)
    stem = pathlib.Path(resultado.get("arquivo") or caminho).stem
    escritos: List[str] = []
    tem_parte_nao_verificada = any(a.get("tecnica") == "nao_verificado"
                                   for a in resultado.get("achados", []))
    if neutralizar:
        texto, n = gerar_neutralizado(caminho, resultado)
        destino_arq = os.path.join(destino, f"{stem}.neutralizado.txt")
        if texto is None:
            extra = "Itens removidos    : (não gerado — OCR indisponível)"
            corpo = ("Não foi possível gerar a cópia neutralizada: OCR (tesseract) indisponível "
                     "para esta imagem. Nunca emitimos cópia 'segura' não verificada.")
        else:
            extra = f"Itens removidos    : {n}"
            if casar_injecao(normalizar(texto)):
                extra += "\nATENÇÃO: possível comando residual (multi-linha) — revise manualmente."
            corpo = texto
        if tem_parte_nao_verificada:
            extra += "\nATENÇÃO: partes do documento não puderam ser lidas e foram omitidas desta cópia."
        with open(destino_arq, "w", encoding="utf-8") as f:
            f.write(_cabecalho(resultado, "CÓPIA NEUTRALIZADA (texto visível; conteúdo oculto removido)", extra))
            f.write(corpo + "\n")
        escritos.append(destino_arq)
    if extrair_oculto:
        corpo, n = gerar_extracao_oculta(resultado)
        destino_arq = os.path.join(destino, f"{stem}.conteudo-oculto.txt")
        with open(destino_arq, "w", encoding="utf-8") as f:
            f.write(_cabecalho(resultado, "CONTEÚDO OCULTO / SUSPEITO EXTRAÍDO (o que estava escrito)",
                               f"Itens extraídos    : {n}"))
            f.write(corpo + "\n")
        escritos.append(destino_arq)
    return escritos
