from __future__ import annotations
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from verificar import doctor

def test_doctor_retorna_lista_sem_fitz_faltando():
    faltando = doctor()
    assert isinstance(faltando, list)
    assert "fitz" not in faltando
