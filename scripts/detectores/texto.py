# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
import pathlib
from achados import Achado
from severidade import para
from padroes_injecao import casar_injecao
from normalizacao import varrer_caracteres, normalizar

def analisar_texto(caminho: str) -> list[Achado]:
    bruto = pathlib.Path(caminho).read_text(encoding="utf-8", errors="replace")
    achados = varrer_caracteres(bruto, local="documento")
    for a in achados:
        if a.decodificado and casar_injecao(normalizar(a.decodificado)):
            a.severidade = para(a.tecnica, True)
    if casar_injecao(normalizar(bruto)):
        achados.append(Achado(tecnica="texto_visivel", severidade=para("texto_visivel", True),
                              local="documento", trecho="<comando dirigido a IA no texto>"))
    return achados
