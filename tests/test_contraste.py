from __future__ import annotations
import sys, pathlib
RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
from PIL import Image
from contraste import faixa_luminancia


def test_preto_sobre_branco_e_alto_contraste():
    img = Image.new("L", (10, 10), 255)
    px = img.load()
    for y in range(10):
        for x in range(5, 10):
            px[x, y] = 0
    assert faixa_luminancia(px, 10, 10, 0, 0, 10, 10) >= 200


def test_cinza_247_sobre_branco_e_baixo_contraste():
    img = Image.new("L", (10, 10), 255)
    px = img.load()
    for y in range(10):
        for x in range(5, 10):
            px[x, y] = 247
    assert faixa_luminancia(px, 10, 10, 0, 0, 10, 10) < 24


def test_bbox_degenerada_retorna_255():
    img = Image.new("L", (10, 10), 255)
    px = img.load()
    assert faixa_luminancia(px, 10, 10, 5, 5, 5, 5) == 255.0
