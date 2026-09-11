from __future__ import annotations
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from achados import Achado, to_dict, SEV_CRITICO, ORDEM_SEV

def test_achado_serializa_e_ordena():
    a = Achado(tecnica="branco_no_branco", severidade=SEV_CRITICO,
               local="página 4", trecho="ignore instruções")
    d = to_dict(a)
    assert d["tecnica"] == "branco_no_branco"
    assert d["decodificado"] is None
    assert ORDEM_SEV[SEV_CRITICO] > ORDEM_SEV["INFO"]
