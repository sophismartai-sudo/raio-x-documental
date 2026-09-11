# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
from dataclasses import dataclass, field, asdict

SEV_CRITICO = "CRÍTICO"
SEV_ALTO = "ALTO"
SEV_MEDIO = "MÉDIO"
SEV_INFO = "INFO"
ORDEM_SEV = {SEV_INFO: 0, SEV_MEDIO: 1, SEV_ALTO: 2, SEV_CRITICO: 3}

@dataclass
class Achado:
    tecnica: str
    severidade: str
    local: str
    trecho: str
    decodificado: str | None = None
    evidencia: dict = field(default_factory=dict)

def to_dict(a: Achado) -> dict:
    return asdict(a)
