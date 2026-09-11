# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
import re
from achados import Achado
from severidade import para
from padroes_injecao import casar_injecao
from normalizacao import varrer_caracteres, normalizar

def _limpar_controles(rtf: str) -> str:
    s = re.sub(r"\\'[0-9a-fA-F]{2}", "", rtf)       # bytes escapados
    s = re.sub(r"\\[a-zA-Z]+-?\d* ?", " ", s)        # control words
    s = s.replace("{", " ").replace("}", " ")
    return re.sub(r"\s+", " ", s).strip()

def analisar_rtf(caminho: str) -> list[Achado]:
    with open(caminho, "r", encoding="latin-1", errors="replace") as f:
        rtf = f.read()
    achados: list[Achado] = []
    # trechos ocultos: após \v (hidden) até \v0 ou fim de grupo
    for seg in re.findall(r"\\v\b(?!0)(.*?)(?:\\v0\b|\})", rtf, re.S):
        texto = _limpar_controles(seg)
        if texto:
            injecao = bool(casar_injecao(normalizar(texto)))
            achados.append(Achado(tecnica="texto_oculto", severidade=para("texto_oculto", injecao),
                                  local="documento", trecho=texto))
    achados.extend(varrer_caracteres(_limpar_controles(rtf), local="documento"))
    return achados
