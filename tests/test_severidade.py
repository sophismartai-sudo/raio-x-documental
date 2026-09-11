from __future__ import annotations
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from severidade import para, veredito
from achados import Achado, SEV_CRITICO, SEV_ALTO, SEV_MEDIO, SEV_INFO

def test_oculto_mais_injecao_e_critico():
    assert para("branco_no_branco", True) == SEV_CRITICO

def test_oculto_sem_injecao_e_medio():
    assert para("branco_no_branco", False) == SEV_MEDIO

def test_injecao_sem_ocultacao_e_alto():
    assert para("texto_visivel", True) == SEV_ALTO

def test_veredito_pega_maior_severidade():
    achs = [Achado("x", SEV_MEDIO, "p1", "t"), Achado("y", SEV_CRITICO, "p2", "t")]
    assert veredito(achs) == SEV_CRITICO

def test_veredito_limpo_quando_vazio():
    assert veredito([]) == "LIMPO"

def test_texto_oculto_e_ocultacao():
    assert para("texto_oculto", True) == SEV_CRITICO
    assert para("texto_oculto", False) == SEV_MEDIO

def test_baixo_contraste_e_ocultacao():
    assert para("baixo_contraste", True) == SEV_CRITICO
    assert para("baixo_contraste", False) == SEV_MEDIO
