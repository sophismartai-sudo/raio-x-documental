# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
import datetime
import html
import json
import pathlib
from typing import Callable, List, Tuple

from achados import ORDEM_SEV

# Nunca importa verificar.py (evita import circular: verificar.py importa este
# módulo). Quem chama passa a função de verificação e o predicado de suporte.

_VERSAO_PADRAO = "raio-x-documental 0.1"

_LIXO_DE_SO_EXATO = {".DS_Store", "Thumbs.db", "desktop.ini"}
_MOTIVO_FORA_DA_PASTA = "atalho/link que aponta para fora da pasta selecionada — não seguido"
_MOTIVO_NAO_REGULAR = "arquivo não regular (não é um arquivo comum) — não analisado"
_MOTIVO_FORMATO = "formato não suportado"


def _eh_lixo_de_so(nome: str) -> bool:
    return nome in _LIXO_DE_SO_EXATO or nome.startswith("._")


def listar(pasta: pathlib.Path, suportado: Callable[[str], bool]) -> dict:
    """Lista SOMENTE os filhos diretos de `pasta` — nunca recursa em subpastas.

    Um atalho/link que aponte para fora da pasta selecionada NUNCA é seguido
    (mesmo que o nome pareça um arquivo de sistema): é sempre listado em
    "ignorados", nunca analisado silenciosamente.
    """
    pasta = pathlib.Path(pasta)
    pasta_resolvida = pasta.resolve()
    documentos: List[pathlib.Path] = []
    ignorados: List[Tuple[str, str]] = []
    subpastas: List[str] = []

    for filho in sorted(pasta.iterdir()):
        if filho.is_dir():
            subpastas.append(filho.name)
            continue
        try:
            real = filho.resolve()
        except OSError:
            ignorados.append((filho.name, _MOTIVO_NAO_REGULAR))
            continue
        if real.parent != pasta_resolvida:
            ignorados.append((filho.name, _MOTIVO_FORA_DA_PASTA))
            continue
        if not real.is_file():
            ignorados.append((filho.name, _MOTIVO_NAO_REGULAR))
            continue
        if _eh_lixo_de_so(filho.name):
            continue
        if suportado(filho.name):
            documentos.append(real)
        else:
            ignorados.append((filho.name, _MOTIVO_FORMATO))

    return {"documentos": documentos, "ignorados": ignorados, "subpastas": subpastas}


def verificar_pasta(pasta: pathlib.Path, verificar_fn: Callable[[str], dict],
                    suportado: Callable[[str], bool]) -> dict:
    """Analisa cada documento encontrado diretamente em `pasta` (nunca subpastas).

    Um erro ao analisar um documento (arquivo corrompido, formato inesperado
    etc.) nunca aborta a execução: vira uma entrada em "erros" e a análise dos
    demais documentos continua normalmente.
    """
    pasta = pathlib.Path(pasta)
    info = listar(pasta, suportado)
    resultados: List[dict] = []
    erros: List[dict] = []
    for real in info["documentos"]:
        try:
            resultado = verificar_fn(str(real))
        except Exception as e:
            erros.append({"arquivo": real.name, "erro": str(e)})
            continue
        resultados.append({**resultado, "caminho": str(real)})
    return {
        "pasta": str(pasta.resolve()),
        "resultados": resultados,
        "erros": erros,
        "ignorados": info["ignorados"],
        "subpastas": info["subpastas"],
    }


_RES_ROTULO_LARGURA = 16


def _rotulo(texto: str) -> str:
    return texto.ljust(_RES_ROTULO_LARGURA)


def imprimir_resumo(res: dict) -> None:
    """Imprime o resumo da pasta em texto puro (sem emojis — consoles Windows)."""
    resultados = res["resultados"]
    erros = res["erros"]
    ignorados = res["ignorados"]
    subpastas = res["subpastas"]

    limpos = [r for r in resultados if r["veredito"] == "LIMPO"]
    suspeitos = [r for r in resultados if r["veredito"] != "LIMPO"]

    print(f"{_rotulo('Pasta analisada')}: {res['pasta']}")
    print(f"{_rotulo('Documentos')}: {len(resultados)} analisados | {len(limpos)} limpos | "
          f"{len(suspeitos)} com achados | {len(erros)} não verificados | {len(ignorados)} ignorados")
    print()
    print("=== DOCUMENTOS COM CONTEÚDO MALICIOSO OU SUSPEITO ===")
    if not suspeitos:
        print("Nenhum documento com conteúdo malicioso ou suspeito.")
    else:
        for r in sorted(suspeitos, key=lambda r: ORDEM_SEV.get(r["veredito"], 0), reverse=True):
            print(f"[{r['veredito']}] {r['arquivo']}")
            for a in r["achados"]:
                if a["severidade"] == "INFO":
                    continue
                print(f"    [{a['severidade']}] {a['tecnica']} @ {a['local']}: {a['trecho'][:80]}")

    if limpos:
        print("Limpos: " + ", ".join(r["arquivo"] for r in limpos))
    if erros:
        print("Não verificados (erro ao ler): " +
              ", ".join(f"{e['arquivo']} — {e['erro']}" for e in erros))
    if ignorados:
        print("Ignorados: " + ", ".join(f"{nome} ({motivo})" for nome, motivo in ignorados))
    if subpastas:
        print("Subpastas NÃO analisadas (só a pasta selecionada é verificada): " +
              ", ".join(subpastas))


def _versao_ferramenta(res: dict) -> str:
    for r in res.get("resultados", []):
        versao = r.get("ferramenta_versao")
        if versao:
            return versao
    return _VERSAO_PADRAO


def _estilo_severidade(veredito: str) -> str:
    return {
        "CRÍTICO": "color:#b00020;font-weight:bold",
        "ALTO": "color:#c05a00;font-weight:bold",
        "MÉDIO": "color:#8a6d00",
        "LIMPO": "color:#0a7a2f",
    }.get(veredito, "")


def _linha_documento(r: dict) -> str:
    nome = html.escape(r["arquivo"])
    estilo = _estilo_severidade(r["veredito"])
    if r["veredito"] != "LIMPO":
        stem = pathlib.Path(r["arquivo"]).stem
        href = html.escape(f"{r['arquivo']}/laudo_{stem}.html", quote=True)
        laudo_html = f'<a href="{href}">laudo</a>'
    else:
        laudo_html = "-"
    return (f"<tr><td>{nome}</td><td style=\"{estilo}\">{html.escape(r['veredito'])}</td>"
            f"<td>{len(r['achados'])}</td><td><code>{html.escape(r['sha256'])}</code></td>"
            f"<td>{laudo_html}</td></tr>")


def _secao_lista(titulo: str, itens: list, texto_item) -> str:
    if not itens:
        return ""
    corpo = "".join(f"<li>{texto_item(item)}</li>" for item in itens)
    return f"<h2>{html.escape(titulo)}</h2><ul>{corpo}</ul>"


def _gerar_html_resumo(res: dict) -> str:
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    resultados = res["resultados"]
    suspeitos = sorted((r for r in resultados if r["veredito"] != "LIMPO"),
                       key=lambda r: ORDEM_SEV.get(r["veredito"], 0), reverse=True)
    limpos = sorted((r for r in resultados if r["veredito"] == "LIMPO"),
                    key=lambda r: r["arquivo"])
    linhas = "".join(_linha_documento(r) for r in (suspeitos + limpos)) or \
        '<tr><td colspan="5">Nenhum documento analisado.</td></tr>'

    secao_erros = _secao_lista("Não verificados (erro ao ler)", res["erros"],
                               lambda e: f"{html.escape(e['arquivo'])} — {html.escape(e['erro'])}")
    secao_ignorados = _secao_lista("Ignorados", res["ignorados"],
                                   lambda item: f"{html.escape(item[0])} ({html.escape(item[1])})")
    secao_subpastas = _secao_lista("Subpastas NÃO analisadas", res["subpastas"],
                                   lambda nome: html.escape(nome))

    return f"""<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<title>Resumo da Pasta</title>
<body style="font-family:Georgia,serif;max-width:1000px;margin:40px auto;color:#111">
<h1>Resumo da Verificação da Pasta</h1>
<p><b>Pasta analisada:</b> {html.escape(res['pasta'])}<br>
<b>Data/hora:</b> {agora}<br>
<b>Ferramenta:</b> {html.escape(_versao_ferramenta(res))}</p>
<h2>Documentos</h2>
<table border="1" cellpadding="6" cellspacing="0" width="100%">
<tr><th>Documento</th><th>Veredito</th><th>Nº de achados</th><th>SHA-256</th><th>Laudo</th></tr>
{linhas}
</table>
{secao_erros}
{secao_ignorados}
{secao_subpastas}
</body></html>"""


def salvar_resumo(res: dict, destino: pathlib.Path) -> Tuple[str, str]:
    """Grava resumo_da_pasta.html e .json em `destino`. Retorna os dois caminhos."""
    destino = pathlib.Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    html_path = destino / "resumo_da_pasta.html"
    json_path = destino / "resumo_da_pasta.json"
    html_path.write_text(_gerar_html_resumo(res), encoding="utf-8")
    json_path.write_text(json.dumps(res, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return str(html_path), str(json_path)
