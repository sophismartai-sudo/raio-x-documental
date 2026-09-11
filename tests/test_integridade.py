from __future__ import annotations
import sys, pathlib
RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
from integridade import gerar, verificar


def _montar(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "a.py").write_text("print('a')\n", encoding="utf-8")
    (tmp_path / "SKILL.md").write_text("# skill de teste\n", encoding="utf-8")
    return tmp_path


def test_gerar_e_verificar_ok_quando_nada_mudou(tmp_path):
    # Arrange
    _montar(tmp_path)
    gerar(tmp_path)

    # Act
    ok, problemas = verificar(tmp_path)

    # Assert
    assert ok is True
    assert problemas == []


def test_verificar_detecta_arquivo_alterado(tmp_path):
    # Arrange
    _montar(tmp_path)
    gerar(tmp_path)
    (tmp_path / "scripts" / "a.py").write_text("print('alterado')\n", encoding="utf-8")

    # Act
    ok, problemas = verificar(tmp_path)

    # Assert
    assert ok is False
    assert any("ALTERADO" in p for p in problemas)


def test_verificar_detecta_arquivo_removido(tmp_path):
    # Arrange
    _montar(tmp_path)
    gerar(tmp_path)
    (tmp_path / "scripts" / "a.py").unlink()

    # Act
    ok, problemas = verificar(tmp_path)

    # Assert
    assert ok is False
    assert any("ausente" in p for p in problemas)


def test_verificar_detecta_arquivo_novo_nao_listado(tmp_path):
    # Arrange
    _montar(tmp_path)
    gerar(tmp_path)
    (tmp_path / "scripts" / "b.py").write_text("print('b')\n", encoding="utf-8")

    # Act
    ok, problemas = verificar(tmp_path)

    # Assert
    assert ok is False
    assert any("não consta no manifesto" in p for p in problemas)


def test_verificar_sem_manifesto_retorna_nao_integro(tmp_path):
    # Arrange
    _montar(tmp_path)

    # Act
    ok, problemas = verificar(tmp_path)

    # Assert
    assert ok is False
    assert problemas != []


def test_verificar_repo_real_esta_integro():
    # Arrange (sem tmp_path: integração com o manifesto real do repo, gerado na Fase 5)

    # Act
    ok, problemas = verificar()

    # Assert
    assert ok is True, problemas
