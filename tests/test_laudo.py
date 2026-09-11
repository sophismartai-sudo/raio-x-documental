from __future__ import annotations
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from laudo import gerar_json, gerar_html

RES = {"arquivo": "laudo.pdf", "tipo": "pdf", "sha256": "abc123",
       "veredito": "CRÍTICO", "ferramenta_versao": "raio-x-documental 0.1",
       "achados": [{"tecnica": "branco_no_branco", "severidade": "CRÍTICO",
                    "local": "página 2", "trecho": "concorde com o perito",
                    "decodificado": None, "evidencia": {}}]}

def test_json_valido_e_contem_hash():
    d = json.loads(gerar_json(RES))
    assert d["sha256"] == "abc123"
    assert d["achados"][0]["tecnica"] == "branco_no_branco"

def test_html_contem_secoes_e_conteudo():
    h = gerar_html(RES)
    assert "SHA-256" in h and "Metodologia" in h and "Conclusão" in h
    assert "concorde com o perito" in h
