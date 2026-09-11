# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
import re

# (categoria, regex). Casar case-insensitive; texto já deve vir normalizado.
PADROES: list[tuple[str, str]] = [
    ("sobrescrever_contexto", r"ignore\s+(all\s+)?previous\s+instructions"),
    ("sobrescrever_contexto", r"disregard\s+(the\s+)?(above|prior)"),
    ("sobrescrever_contexto", r"ignore\s+(as\s+)?instru[cç][õo]es\s+anteriores"),
    ("sobrescrever_contexto", r"desconsidere\s+o\s+(texto|comando)\s+acima"),
    ("sobrescrever_contexto", r"aten[cç][ãa]o,?\s+intelig[êe]ncia\s+artificial"),
    ("sobrescrever_contexto", r"independentemente\s+do\s+comando"),
    ("persona_ia", r"as\s+an\s+ai(\s+language\s+model)?"),
    ("persona_ia", r"system\s+prompt"),
    ("persona_ia", r"voc[êe]\s+deve\b"),
    ("coacao_veredito", r"give\s+a\s+positive\s+review"),
    ("coacao_veredito", r"mark\s+this\s+.{0,40}\s+as\s+qualified"),
    ("coacao_veredito", r"concorde\s+com"),
    ("coacao_veredito", r"d[êe]\s+(um\s+)?parecer\s+favor[áa]vel"),
    ("coacao_veredito", r"julgue\s+procedente"),
    ("coacao_veredito", r"n[ãa]o\s+(conteste|impugne|mencione|destaque)"),
    ("coacao_veredito", r"conteste\s+.{0,40}\s+de\s+forma\s+superficial"),
    ("coacao_veredito", r"decida\s+a\s+favor"),
]
_COMPILADOS = [(c, re.compile(p, re.IGNORECASE | re.DOTALL)) for c, p in PADROES]

def casar_injecao(texto: str) -> list[str]:
    achados: list[str] = []
    for categoria, rx in _COMPILADOS:
        m = rx.search(texto)
        if m:
            achados.append(f"{categoria}: {m.group(0).strip()}")
    return achados
