from __future__ import annotations
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from normalizacao import normalizar, decodificar_tags, varrer_caracteres

def test_normalizar_remove_zero_width():
    assert normalizar("con​corde") == "concorde"

def test_decodifica_unicode_tags():
    escondido = chr(0xE0000 + ord("o")) + chr(0xE0000 + ord("i"))
    assert decodificar_tags(escondido) == "oi"

def test_varre_tags_gera_achado_com_decodificado():
    escondido = "".join(chr(0xE0000 + ord(c)) for c in "aprove")
    achs = varrer_caracteres(escondido, local="texto")
    assert any(a.tecnica == "unicode_tags" for a in achs)
    assert any(a.decodificado == "aprove" for a in achs)

def test_texto_limpo_nao_gera_achado():
    assert varrer_caracteres("texto normal do processo") == []
