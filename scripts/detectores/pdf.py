# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
import io
import fitz  # PyMuPDF
from PIL import Image
from achados import Achado
from severidade import para
from padroes_injecao import casar_injecao
from normalizacao import varrer_caracteres, normalizar
from detectores.imagem import analisar_imagem_pil

FONTE_MIN_PT = 2.0
BRANCO_MIN = 245  # canais >= isto ≈ branco
CONTRASTE_MIN = 24.0  # diferença de luminância 0-255 medida no pixel renderizado
PDF_OCR_MAX_CHARS = 20  # página com menos texto extraível que isto é tratada como escaneada

def _int_para_rgb(cor: int) -> tuple[int, int, int]:
    return ((cor >> 16) & 255, (cor >> 8) & 255, cor & 255)

def _eh_branco(cor: int) -> bool:
    r, g, b = _int_para_rgb(cor)
    return r >= BRANCO_MIN and g >= BRANCO_MIN and b >= BRANCO_MIN

def _fora_da_pagina(bbox, rect) -> bool:
    x0, y0, x1, y1 = bbox
    return x1 < rect.x0 or x0 > rect.x1 or y1 < rect.y0 or y0 > rect.y1

def _contraste_bbox(pix, bbox, sc: float) -> float:
    x0, y0 = int(bbox[0]*sc), int(bbox[1]*sc)
    x1, y1 = int(bbox[2]*sc), int(bbox[3]*sc)
    x0 = max(0, x0); y0 = max(0, y0); x1 = min(pix.width, x1); y1 = min(pix.height, y1)
    if x1 <= x0 or y1 <= y0:
        return 255.0
    n, stride, sm = pix.n, pix.stride, pix.samples
    lmin, lmax, passo = 255.0, 0.0, 2
    for y in range(y0, y1, passo):
        base = y * stride
        for x in range(x0, x1, passo):
            i = base + x * n
            lum = 0.299*sm[i] + 0.587*sm[i+1] + 0.114*sm[i+2]
            if lum < lmin: lmin = lum
            if lum > lmax: lmax = lum
    return lmax - lmin

def analisar_pdf(caminho: str) -> list[Achado]:
    achados: list[Achado] = []
    doc = fitz.open(caminho)
    try:
        for i, page in enumerate(doc, start=1):
            local = f"página {i}"
            pix = page.get_pixmap(alpha=False)
            sc = pix.width / page.rect.width if page.rect.width else 1.0
            dados = page.get_text("dict")
            for bloco in dados.get("blocks", []):
                for linha in bloco.get("lines", []):
                    for span in linha.get("spans", []):
                        txt = span.get("text", "")
                        if not txt.strip():
                            continue
                        tecnica = None
                        if _eh_branco(span.get("color", 0)) and _contraste_bbox(pix, span.get("bbox", (0, 0, 0, 0)), sc) < CONTRASTE_MIN:
                            tecnica = "branco_no_branco"
                        elif span.get("size", 99) < FONTE_MIN_PT:
                            tecnica = "fonte_minuscula"
                        elif _fora_da_pagina(span.get("bbox", (0, 0, 0, 0)), page.rect):
                            tecnica = "fora_da_pagina"
                        if tecnica:
                            injecao = bool(casar_injecao(normalizar(txt)))
                            achados.append(Achado(
                                tecnica=tecnica, severidade=para(tecnica, injecao),
                                local=local, trecho=txt.strip(),
                                evidencia={"cor": span.get("color"), "tamanho": span.get("size")}))
            texto_pagina = page.get_text("text")
            achados.extend(varrer_caracteres(texto_pagina, local=local))
            if len(texto_pagina.strip()) < PDF_OCR_MAX_CHARS:
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                achados.extend(analisar_imagem_pil(img, local=f"{local} (escaneada)"))
        for chave, valor in (doc.metadata or {}).items():
            if valor and len(str(valor)) > 200:
                injecao = bool(casar_injecao(normalizar(str(valor))))
                achados.append(Achado(tecnica="metadados", severidade=para("metadados", injecao),
                                      local=f"metadados/{chave}", trecho=str(valor)[:500]))
    finally:
        doc.close()
    return achados
