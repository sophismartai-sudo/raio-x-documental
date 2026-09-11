# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
import unicodedata
from achados import Achado, SEV_MEDIO

RUN_INVISIVEL_MIN = 8
INVISIVEIS = {0x200B, 0x200C, 0x200D, 0xFEFF, 0x2060, 0x00AD, 0x180E}
BIDI = {0x202A, 0x202B, 0x202C, 0x202D, 0x202E, 0x2066, 0x2067, 0x2068, 0x2069, 0x200E, 0x200F, 0x061C}
TAG_INI, TAG_FIM = 0xE0000, 0xE007F

def _eh_tag(cp: int) -> bool:
    return TAG_INI <= cp <= TAG_FIM

def decodificar_tags(texto: str) -> str:
    out = []
    for ch in texto:
        cp = ord(ch)
        if _eh_tag(cp):
            base = cp - TAG_INI
            if 0x20 <= base <= 0x7E:
                out.append(chr(base))
        else:
            out.append(ch)
    return "".join(out)

def normalizar(texto: str) -> str:
    limpo = "".join(ch for ch in texto if ord(ch) not in INVISIVEIS and ord(ch) not in BIDI)
    limpo = decodificar_tags(limpo)
    return unicodedata.normalize("NFKC", limpo)

def varrer_caracteres(texto: str, local: str = "texto") -> list[Achado]:
    achados: list[Achado] = []
    tags = [ch for ch in texto if _eh_tag(ord(ch))]
    if tags:
        dec = decodificar_tags("".join(tags))
        achados.append(Achado(tecnica="unicode_tags", severidade=SEV_MEDIO, local=local,
                              trecho="<tags unicode invisíveis>", decodificado=dec,
                              evidencia={"quantidade": len(tags)}))
    invis = [ch for ch in texto if ord(ch) in INVISIVEIS]
    if len(invis) >= RUN_INVISIVEL_MIN:
        achados.append(Achado(tecnica="zero_width", severidade=SEV_MEDIO, local=local,
                              trecho="<caracteres de largura zero>", evidencia={"quantidade": len(invis)}))
    bidi = [ch for ch in texto if ord(ch) in BIDI]
    if bidi:
        achados.append(Achado(tecnica="bidi", severidade=SEV_MEDIO, local=local,
                              trecho="<override bidirecional>", evidencia={"quantidade": len(bidi)}))
    return achados
