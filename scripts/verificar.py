# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
import hashlib, pathlib, argparse, shutil, subprocess, sys
from achados import to_dict, SEV_CRITICO, SEV_ALTO
from severidade import veredito
from detectores.pdf import analisar_pdf
from detectores.texto import analisar_texto
from detectores.docx import analisar_docx
from detectores.odt import analisar_odt
from detectores.rtf import analisar_rtf
from detectores.html_email import analisar_html
from detectores.imagem import analisar_imagem
from detectores import imagem as _imagem_mod
from laudo import salvar
from higienizacao import higienizar

VERSAO = "raio-x-documental 0.1"

def doctor() -> list[str]:
    faltando = []
    for mod in ("fitz", "lxml", "PIL", "docx"):
        try:
            __import__(mod)
        except Exception:
            faltando.append(mod)
    return faltando

def ocr_status() -> str:
    binp = _imagem_mod._tesseract()
    if not binp:
        return "OCR: tesseract AUSENTE — imagens e PDF escaneado NÃO serão verificados (instale o tesseract)."
    try:
        out = subprocess.run([binp, "--list-langs"], capture_output=True, text=True, timeout=30).stdout
        langs = [l for l in ("por", "eng") if l in out.split()]
    except Exception:
        langs = []
    return f"OCR: tesseract OK ({binp}); idiomas p/ laudo: {', '.join(langs) or 'nenhum (por/eng) — instale tessdata'}."

_EXT = {".pdf": "pdf", ".txt": "txt", ".md": "txt",
        ".docx": "docx", ".doc": "docx", ".odt": "odt", ".rtf": "rtf",
        ".html": "html", ".htm": "html", ".eml": "html",
        ".png": "imagem", ".jpg": "imagem", ".jpeg": "imagem",
        ".tif": "imagem", ".tiff": "imagem", ".bmp": "imagem", ".webp": "imagem"}

def sha256(caminho: str) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()

def detectar_formato(caminho: str) -> str:
    return _EXT.get(pathlib.Path(caminho).suffix.lower(), "desconhecido")

def verificar(caminho: str) -> dict:
    tipo = detectar_formato(caminho)
    _DISPATCH = {"pdf": analisar_pdf, "txt": analisar_texto, "docx": analisar_docx,
                 "odt": analisar_odt, "rtf": analisar_rtf, "html": analisar_html,
                 "imagem": analisar_imagem}
    fn = _DISPATCH.get(tipo)
    if fn is None:
        raise ValueError(f"Formato ainda não suportado: {tipo}")
    achados = fn(caminho)
    return {
        "arquivo": pathlib.Path(caminho).name,
        "tipo": tipo,
        "sha256": sha256(caminho),
        "ferramenta_versao": VERSAO,
        "veredito": veredito(achados),
        "achados": [to_dict(a) for a in achados],
    }

def _imprimir(r: dict) -> None:
    print(f"Arquivo : {r['arquivo']}  ({r['tipo']})")
    print(f"SHA-256 : {r['sha256']}")
    print(f"Veredito: {r['veredito']}")
    for a in r["achados"]:
        print(f"  [{a['severidade']}] {a['tecnica']} @ {a['local']}: {a['trecho'][:80]}")

def _main_pasta(caminho: pathlib.Path, args: argparse.Namespace) -> int:
    """Modo pasta: analisa só os documentos diretamente dentro de `caminho`."""
    import pasta
    caminho_resolvido = caminho.resolve()
    destinos = [d for d in (args.laudo, args.higienizar) if d]
    if any(pathlib.Path(d).resolve() == caminho_resolvido for d in destinos):
        print("Erro: a pasta de resultados não pode ser a mesma pasta analisada. "
              "Escolha outra pasta para os resultados.")
        return 2
    res = pasta.verificar_pasta(caminho, verificar, lambda n: detectar_formato(n) != "desconhecido")
    pasta.imprimir_resumo(res)
    suspeitos = [r for r in res["resultados"] if r["veredito"] != "LIMPO"]
    if args.laudo:
        for r in suspeitos:
            salvar(r, str(pathlib.Path(args.laudo) / r["arquivo"]))
        h, _j = pasta.salvar_resumo(res, pathlib.Path(args.laudo))
        print(f"Resumo: {h}")
    if args.higienizar:
        neutralizar = args.modo in ("neutralizar", "ambos")
        extrair = args.modo in ("revelar", "ambos")
        for r in suspeitos:
            higienizar(r["caminho"], r, str(pathlib.Path(args.higienizar) / r["arquivo"]),
                      neutralizar=neutralizar, extrair_oculto=extrair)
    if suspeitos and not args.laudo and not args.higienizar:
        print("Dica: rode com --laudo <pasta de resultados> e/ou --higienizar <pasta de resultados> "
              "para gerar laudos e/ou cópias higienizadas dos documentos suspeitos (não altera os originais).")
    if any(r["veredito"] in (SEV_CRITICO, SEV_ALTO) for r in res["resultados"]):
        return 1
    if res["erros"]:
        return 2
    return 0


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="raio-x-documental: detecta texto oculto / prompt injection.")
    ap.add_argument("arquivo", nargs="?")
    ap.add_argument("--laudo", metavar="DIR", help="gera laudo HTML/JSON neste diretório")
    ap.add_argument("--higienizar", metavar="DIR",
                    help="gera cópia(s) higienizada(s) neste diretório (não altera o original)")
    ap.add_argument("--modo", choices=["neutralizar", "revelar", "ambos"], default="ambos",
                    help="o que gerar ao higienizar: cópia neutralizada, conteúdo oculto revelado, ou ambos")
    ap.add_argument("--doctor", action="store_true", help="verifica dependências e sai")
    ap.add_argument("--verificar-integridade", action="store_true",
                    help="confere a skill contra INTEGRIDADE.sha256")
    args = ap.parse_args(argv)
    if args.doctor:
        faltando = doctor()
        print("Dependências OK." if not faltando else "Faltando: " + ", ".join(faltando))
        print(ocr_status())
        from integridade import verificar as _vi
        ok, _ = _vi()
        print("Integridade: OK" if ok else "Integridade: COMPROMETIDA (rode --verificar-integridade)")
        return 0 if not faltando else 2
    if args.verificar_integridade:
        from integridade import verificar as _vi
        ok, problemas = _vi()
        print("Integridade OK: os arquivos conferem com INTEGRIDADE.sha256."
              if ok else "INTEGRIDADE COMPROMETIDA:")
        for p in problemas:
            print(f"  - {p}")
        return 0 if ok else 2
    if not args.arquivo:
        ap.error("informe o arquivo a verificar")
    caminho = pathlib.Path(args.arquivo)
    if not caminho.exists():
        print(f"Arquivo ou pasta não encontrado: {args.arquivo}")
        return 2
    if caminho.is_dir():
        return _main_pasta(caminho, args)
    try:
        r = verificar(args.arquivo)
    except Exception as e:
        print(f"Não foi possível analisar o arquivo: {e}. Documento NÃO verificado.")
        return 2
    _imprimir(r)
    if args.laudo:
        h, j = salvar(r, args.laudo)
        print(f"Laudo: {h}\nJSON : {j}")
    if args.higienizar:
        neutralizar = args.modo in ("neutralizar", "ambos")
        extrair = args.modo in ("revelar", "ambos")
        for p in higienizar(args.arquivo, r, args.higienizar,
                            neutralizar=neutralizar, extrair_oculto=extrair):
            print(f"Higienização: {p}")
    elif r["veredito"] != "LIMPO":
        print("Dica: rode com --higienizar <dir> [--modo neutralizar|revelar|ambos] para gerar "
              "uma cópia neutralizada e/ou extrair exatamente o conteúdo oculto (não altera o original).")
    return 1 if r["veredito"] in (SEV_CRITICO, SEV_ALTO) else 0

if __name__ == "__main__":
    raise SystemExit(main())
