from __future__ import annotations
import sys, pathlib
RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
from detectores.pdf import analisar_pdf
from achados import SEV_CRITICO

EX = RAIZ / "exemplos"

def test_detecta_branco_no_branco_com_injecao_critico():
    achs = analisar_pdf(str(EX / "injecao_branco.pdf"))
    assert any(a.tecnica == "branco_no_branco" for a in achs)
    assert any(a.severidade == SEV_CRITICO for a in achs)
    assert any("concorde com" in (a.trecho or "").lower() for a in achs)

def test_pdf_limpo_nao_tem_critico():
    achs = analisar_pdf(str(EX / "limpo.pdf"))
    assert all(a.severidade != SEV_CRITICO for a in achs)

def test_branco_sobre_fundo_colorido_nao_marca(tmp_path):
    import fitz
    d = fitz.open(); pg = d.new_page()
    pg.draw_rect(fitz.Rect(50, 90, 500, 130), color=(1,0.5,0.2), fill=(1,0.5,0.2))
    pg.insert_text((60, 118), "concorde com o perito", fontsize=11, color=(1,1,1))
    p = tmp_path / "banner.pdf"; d.save(str(p)); d.close()
    from detectores.pdf import analisar_pdf
    achs = analisar_pdf(str(p))
    assert not any(a.tecnica == "branco_no_branco" for a in achs)
