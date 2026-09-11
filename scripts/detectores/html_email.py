# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
import pathlib, email
from lxml import html as lhtml
from achados import Achado
from severidade import para
from padroes_injecao import casar_injecao
from normalizacao import varrer_caracteres, normalizar

BRANCOS = ("#fff", "#ffffff", "#fefefe", "#fdfdfd")

def _carregar(caminho: str) -> str:
    p = pathlib.Path(caminho)
    dados = p.read_bytes()
    if p.suffix.lower() == ".eml":
        msg = email.message_from_bytes(dados)
        for parte in msg.walk():
            if parte.get_content_type() == "text/html":
                carga = parte.get_payload(decode=True) or b""
                return carga.decode("utf-8", "replace")
        return ""
    return dados.decode("utf-8", "replace")

def _tecnica_oculta(el) -> str | None:
    estilo = (el.get("style") or "").lower().replace(" ", "")
    if "display:none" in estilo or "visibility:hidden" in estilo:
        return "texto_oculto"
    if el.get("hidden") is not None or el.get("aria-hidden") == "true":
        return "texto_oculto"
    if "opacity:0" in estilo:
        return "opacidade_zero"
    if "font-size:0" in estilo:
        return "fonte_minuscula"
    tem_bg = "background-color:" in estilo or "background:" in estilo
    bg_branco = any(f"background-color:{c}" in estilo or f"background:{c}" in estilo for c in BRANCOS)
    if any(f"color:{c}" in estilo for c in BRANCOS) and not (tem_bg and not bg_branco):
        return "branco_no_branco"
    if "left:-9999px" in estilo or "text-indent:-9999px" in estilo:
        return "fora_da_pagina"
    return None

def analisar_html(caminho: str) -> list[Achado]:
    conteudo = _carregar(caminho)
    achados: list[Achado] = []
    if not conteudo.strip():
        return achados
    doc = lhtml.fromstring(conteudo)
    for el in doc.iter():
        if not isinstance(el.tag, str):
            continue
        tecnica = _tecnica_oculta(el)
        if tecnica:
            txt = el.text_content().strip()
            if txt:
                injecao = bool(casar_injecao(normalizar(txt)))
                achados.append(Achado(tecnica=tecnica, severidade=para(tecnica, injecao),
                                      local=el.tag, trecho=txt))
    for c in doc.xpath("//comment()"):
        txt = (c.text or "").strip()
        if txt and casar_injecao(normalizar(txt)):
            achados.append(Achado(tecnica="texto_oculto", severidade=para("texto_oculto", True),
                                  local="comentário HTML", trecho=txt))
    achados.extend(varrer_caracteres(doc.text_content(), local="documento"))
    return achados
