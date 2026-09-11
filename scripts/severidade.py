# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
from achados import Achado, SEV_CRITICO, SEV_ALTO, SEV_MEDIO, SEV_INFO, ORDEM_SEV

TECNICAS_OCULTACAO = {
    "branco_no_branco", "render_mode_3", "fonte_minuscula", "fora_da_pagina",
    "opacidade_zero", "zero_width", "unicode_tags", "bidi", "texto_oculto",
    "baixo_contraste", "entidade_xml",
}

def para(tecnica: str, injecao_no_trecho: bool) -> str:
    oculto = tecnica in TECNICAS_OCULTACAO
    if oculto and injecao_no_trecho:
        return SEV_CRITICO
    if oculto:
        return SEV_MEDIO
    if injecao_no_trecho:
        return SEV_ALTO
    return SEV_INFO

def veredito(achados: list[Achado]) -> str:
    relevantes = [a for a in achados if a.severidade != SEV_INFO]
    if not relevantes:
        return "LIMPO"
    return max(relevantes, key=lambda a: ORDEM_SEV[a.severidade]).severidade
