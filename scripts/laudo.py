# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
import json, html, pathlib, datetime

def gerar_json(resultado: dict) -> str:
    return json.dumps(resultado, ensure_ascii=False, indent=2)

def _linha_achado(a: dict) -> str:
    dec = f"<br><em>Decodificado:</em> {html.escape(a['decodificado'])}" if a.get("decodificado") else ""
    return (f"<tr><td>{html.escape(a['severidade'])}</td>"
            f"<td>{html.escape(a['tecnica'])}</td>"
            f"<td>{html.escape(a['local'])}</td>"
            f"<td>{html.escape(a['trecho'])}{dec}</td></tr>")

def gerar_html(resultado: dict) -> str:
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    linhas = "".join(_linha_achado(a) for a in resultado["achados"]) or \
        "<tr><td colspan=4>Nenhum achado.</td></tr>"
    return f"""<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<title>Laudo de Verificação — {html.escape(resultado['arquivo'])}</title>
<body style="font-family:Georgia,serif;max-width:800px;margin:40px auto;color:#111">
<h1>Laudo de Verificação de Integridade Documental</h1>
<h2>1. Identificação</h2>
<p><b>Arquivo:</b> {html.escape(resultado['arquivo'])}<br>
<b>Tipo:</b> {html.escape(resultado['tipo'])}<br>
<b>SHA-256:</b> <code>{html.escape(resultado['sha256'])}</code><br>
<b>Data/hora da análise:</b> {agora}</p>
<h2>2. Objeto</h2>
<p>Verificação de conteúdo oculto e comandos de prompt injection no documento.</p>
<h2>3. Metodologia</h2>
<p>Análise determinística e offline por {html.escape(resultado['ferramenta_versao'])}: normalização
Unicode, varredura de contrabando por caractere, extração forense por formato e casamento de padrões
de instrução dirigida a IA.</p>
<h2>4. Achados</h2>
<table border="1" cellpadding="6" cellspacing="0" width="100%">
<tr><th>Gravidade</th><th>Técnica</th><th>Localização</th><th>Conteúdo</th></tr>
{linhas}</table>
<h2>5. Conclusão</h2>
<p><b>Veredito:</b> {html.escape(resultado['veredito'])}.</p>
<h2>6. Ressalvas</h2>
<p>Este laudo documenta indícios técnicos; não imputa dolo. Recomenda-se a intimação prévia da parte
(art. 77, §1º, CPC) antes de qualquer sanção, distinguindo artefato de editoração de manipulação dolosa.</p>
<h2>7. Base normativa</h2>
<p>Res. CNJ 615/2025 (AR2; arts. 19 e 21); Nota Técnica CNIAJ/CNJ; CPC art. 473; CPP art. 158-A (cadeia
de custódia).</p>
<h2>8. Assinatura</h2>
<p>_____________________________________<br>Servidor(a) responsável — assinatura ICP-Brasil.</p>
</body></html>"""

def salvar(resultado: dict, destino: str) -> tuple[str, str]:
    base = pathlib.Path(destino)
    base.mkdir(parents=True, exist_ok=True)
    nome = pathlib.Path(resultado["arquivo"]).stem
    html_path = base / f"laudo_{nome}.html"
    json_path = base / f"laudo_{nome}.json"
    html_path.write_text(gerar_html(resultado), encoding="utf-8")
    json_path.write_text(gerar_json(resultado), encoding="utf-8")
    return str(html_path), str(json_path)
