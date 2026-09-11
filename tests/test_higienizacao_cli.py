from __future__ import annotations
import sys, pathlib
RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

from verificar import main

EX = RAIZ / "exemplos"


def test_modo_ambos_gera_dois_arquivos_e_retorna_critico(tmp_path):
    pdf = EX / "injecao_branco.pdf"

    rc = main([str(pdf), "--higienizar", str(tmp_path), "--modo", "ambos"])

    assert rc == 1
    neutralizado = tmp_path / "injecao_branco.neutralizado.txt"
    oculto = tmp_path / "injecao_branco.conteudo-oculto.txt"
    assert neutralizado.exists()
    assert oculto.exists()
    assert "concorde" not in neutralizado.read_text(encoding="utf-8").lower()
    assert "concorde" in oculto.read_text(encoding="utf-8").lower()


def test_modo_neutralizar_gera_so_o_neutralizado(tmp_path):
    pdf = EX / "injecao_branco.pdf"

    main([str(pdf), "--higienizar", str(tmp_path), "--modo", "neutralizar"])

    assert (tmp_path / "injecao_branco.neutralizado.txt").exists()
    assert not (tmp_path / "injecao_branco.conteudo-oculto.txt").exists()


def test_modo_revelar_gera_so_o_conteudo_oculto(tmp_path):
    pdf = EX / "injecao_branco.pdf"

    main([str(pdf), "--higienizar", str(tmp_path), "--modo", "revelar"])

    assert not (tmp_path / "injecao_branco.neutralizado.txt").exists()
    assert (tmp_path / "injecao_branco.conteudo-oculto.txt").exists()


def test_higienizar_nunca_altera_o_original(tmp_path):
    pdf = EX / "injecao_branco.pdf"
    bytes_antes = pdf.read_bytes()

    main([str(pdf), "--higienizar", str(tmp_path), "--modo", "ambos"])

    assert pdf.read_bytes() == bytes_antes


def test_hint_aparece_quando_ha_achados_e_nao_gera_arquivo(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pdf = EX / "injecao_branco.pdf"

    rc = main([str(pdf)])

    saida = capsys.readouterr().out
    assert "--higienizar" in saida
    assert rc == 1
    assert list(tmp_path.iterdir()) == []


def test_hint_nao_aparece_quando_documento_esta_limpo(capsys):
    pdf = EX / "limpo.pdf"

    rc = main([str(pdf)])

    saida = capsys.readouterr().out
    assert "--higienizar" not in saida
    assert rc == 0
