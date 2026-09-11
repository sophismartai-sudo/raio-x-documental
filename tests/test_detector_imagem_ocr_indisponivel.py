from __future__ import annotations
import sys, pathlib
RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
from detectores import imagem
from detectores.imagem import analisar_imagem_pil

from PIL import Image

# Sem pytestmark/skip guard de propósito: este teste NÃO exige o binário tesseract
# (ele monkeypatcha a checagem embutida) e deve rodar sempre, mesmo sem OCR instalado.


def test_ocr_indisponivel_gera_achado_medio(monkeypatch):
    monkeypatch.setattr(imagem, "_tesseract", lambda: None)
    achados = analisar_imagem_pil(Image.new("RGB", (50, 50), "white"))
    assert len(achados) == 1
    assert achados[0].tecnica == "ocr_indisponivel"
