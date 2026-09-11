# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations


def faixa_luminancia(px, largura: int, altura: int,
                     x0: int, y0: int, x1: int, y1: int, passo: int = 2) -> float:
    """Amplitude de luminância (0-255) numa bbox de imagem PIL modo 'L'.
    `px` é o acessor de PixelAccess (Image.convert('L').load()); px[x,y] -> int 0..255.
    Faixa alta = alto contraste (texto legível); faixa baixa = texto quase invisível."""
    x0 = max(0, x0); y0 = max(0, y0)
    x1 = min(largura, x1); y1 = min(altura, y1)
    if x1 <= x0 or y1 <= y0:
        return 255.0
    lmin, lmax = 255, 0
    for y in range(y0, y1, passo):
        for x in range(x0, x1, passo):
            v = px[x, y]
            if v < lmin:
                lmin = v
            if v > lmax:
                lmax = v
    return float(lmax - lmin)
