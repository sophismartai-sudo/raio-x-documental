from __future__ import annotations
import sys, pathlib
RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
from verificar import verificar, detectar_formato
EX = RAIZ / "exemplos"

def test_verificar_pdf_injetado_da_critico_e_hash():
    r = verificar(str(EX / "injecao_branco.pdf"))
    assert r["veredito"] == "CRÍTICO"
    assert len(r["sha256"]) == 64
    assert r["tipo"] == "pdf"

def test_verificar_pdf_limpo_da_limpo():
    r = verificar(str(EX / "limpo.pdf"))
    assert r["veredito"] == "LIMPO"

def test_detectar_formato_por_extensao(tmp_path):
    p = tmp_path / "a.TXT"; p.write_text("x", encoding="utf-8")
    assert detectar_formato(str(p)) == "txt"
