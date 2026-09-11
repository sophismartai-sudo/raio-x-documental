from __future__ import annotations
import sys, pathlib, os, json
RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

import pytest

from verificar import verificar, detectar_formato, main
import pasta as pasta_mod

EX = RAIZ / "exemplos"


def _suportado(nome: str) -> bool:
    return detectar_formato(nome) != "desconhecido"


def _montar_pasta_basica(base: pathlib.Path) -> pathlib.Path:
    """Pasta com: 1 crítico, 1 limpo, 1 subpasta com um crítico (não deve ser
    analisado), 1 planilha (formato não suportado), 1 .DS_Store (lixo de SO),
    1 arquivo oculto suportado (crítico) e 1 arquivo corrompido."""
    p = base / "pasta"
    p.mkdir()
    (p / "critico.pdf").write_bytes((EX / "injecao_branco.pdf").read_bytes())
    (p / "limpo.pdf").write_bytes((EX / "limpo.pdf").read_bytes())
    sub = p / "sub"
    sub.mkdir()
    (sub / "critico_escondido.pdf").write_bytes((EX / "injecao_branco.pdf").read_bytes())
    (p / "planilha.xlsx").write_bytes(b"PK\x03\x04 nao e realmente um xlsx")
    (p / ".DS_Store").write_bytes(b"lixo do finder")
    (p / ".oculto.pdf").write_bytes((EX / "injecao_branco.pdf").read_bytes())
    (p / "quebrado.pdf").write_bytes(b"nao e pdf")
    return p


def test_listar_analisa_so_filhos_diretos_e_lista_subpasta_sem_entrar(tmp_path):
    p = _montar_pasta_basica(tmp_path)

    info = pasta_mod.listar(p, _suportado)

    nomes_documentos = {d.name for d in info["documentos"]}
    assert "critico_escondido.pdf" not in nomes_documentos
    assert "sub" in info["subpastas"]


def test_symlink_para_fora_da_pasta_nao_e_analisado_e_fica_em_ignorados(tmp_path):
    p = _montar_pasta_basica(tmp_path)
    alvo_externo = tmp_path / "fora_da_pasta.pdf"
    alvo_externo.write_bytes((EX / "injecao_branco.pdf").read_bytes())
    link = p / "atalho.pdf"
    try:
        os.symlink(alvo_externo, link)
    except (OSError, NotImplementedError):
        pytest.skip("criação de symlink não permitida neste ambiente")

    info = pasta_mod.listar(p, _suportado)

    nomes_documentos = {d.name for d in info["documentos"]}
    assert "atalho.pdf" not in nomes_documentos
    nomes_ignorados = {nome for nome, _motivo in info["ignorados"]}
    assert "atalho.pdf" in nomes_ignorados


def test_planilha_xlsx_fica_em_ignorados_por_formato_nao_suportado(tmp_path):
    p = _montar_pasta_basica(tmp_path)

    info = pasta_mod.listar(p, _suportado)

    achado = [m for n, m in info["ignorados"] if n == "planilha.xlsx"]
    assert achado == ["formato não suportado"]


def test_ds_store_nao_aparece_em_nenhuma_lista(tmp_path):
    p = _montar_pasta_basica(tmp_path)

    info = pasta_mod.listar(p, _suportado)

    todos_nomes_ignorados = {n for n, _m in info["ignorados"]}
    nomes_documentos = {d.name for d in info["documentos"]}
    assert ".DS_Store" not in todos_nomes_ignorados
    assert ".DS_Store" not in nomes_documentos


def test_arquivo_oculto_suportado_e_analisado(tmp_path):
    p = _montar_pasta_basica(tmp_path)

    info = pasta_mod.listar(p, _suportado)

    nomes_documentos = {d.name for d in info["documentos"]}
    assert ".oculto.pdf" in nomes_documentos


def test_arquivo_corrompido_cai_em_erros_sem_abortar_a_execucao(tmp_path):
    p = _montar_pasta_basica(tmp_path)

    res = pasta_mod.verificar_pasta(p, verificar, _suportado)

    nomes_erro = {e["arquivo"] for e in res["erros"]}
    assert "quebrado.pdf" in nomes_erro
    # o resto da pasta continuou sendo analisado apesar do arquivo corrompido
    nomes_resultado = {r["arquivo"] for r in res["resultados"]}
    assert "critico.pdf" in nomes_resultado
    assert "limpo.pdf" in nomes_resultado


def test_cli_modo_pasta_reporta_suspeitos_e_retorna_1(tmp_path, capsys):
    p = _montar_pasta_basica(tmp_path)

    rc = main([str(p)])

    saida = capsys.readouterr().out
    assert rc == 1
    assert "DOCUMENTOS COM CONTEÚDO MALICIOSO OU SUSPEITO" in saida
    assert "critico.pdf" in saida


def test_cli_recusa_pasta_de_resultados_igual_a_pasta_analisada(tmp_path, capsys):
    p = _montar_pasta_basica(tmp_path)

    rc = main([str(p), "--laudo", str(p)])

    saida = capsys.readouterr().out
    assert rc == 2
    assert "não pode ser a mesma pasta analisada" in saida
    # nada deve ter sido escrito dentro da própria pasta analisada
    assert not (p / "resumo_da_pasta.html").exists()
    assert not (p / "resumo_da_pasta.json").exists()


def test_cli_laudo_gera_resumo_e_laudos_por_suspeito_sem_marca_autoral(tmp_path):
    p = _montar_pasta_basica(tmp_path)
    bytes_antes = {f.name: f.read_bytes() for f in p.iterdir() if f.is_file()}
    out = tmp_path / "saida"

    rc = main([str(p), "--laudo", str(out)])

    assert rc == 1
    resumo_html = out / "resumo_da_pasta.html"
    resumo_json = out / "resumo_da_pasta.json"
    assert resumo_html.exists()
    assert resumo_json.exists()
    assert (out / "critico.pdf" / "laudo_critico.html").exists()
    assert not (out / "limpo.pdf").exists()          # sem laudo para documento limpo

    conteudo_json = json.loads(resumo_json.read_text(encoding="utf-8"))
    assert conteudo_json["pasta"]

    texto_html = resumo_html.read_text(encoding="utf-8")
    for marca in ("©", "proibid", "licen", "@sophismart", "@agro_murilo"):
        assert marca not in texto_html.lower() and marca not in texto_html

    # originais intactos
    for f in p.iterdir():
        if f.is_file():
            assert f.read_bytes() == bytes_antes[f.name]


def test_cli_pasta_inexistente_retorna_2(tmp_path, capsys):
    alvo = tmp_path / "nao_existe"

    rc = main([str(alvo)])

    saida = capsys.readouterr().out
    assert rc == 2
    assert "não encontrado" in saida


def test_cli_arquivo_unico_formato_nao_suportado_retorna_2_sem_traceback(tmp_path, capsys):
    xlsx = tmp_path / "planilha.xlsx"
    xlsx.write_bytes(b"PK\x03\x04 nao e realmente um xlsx")

    rc = main([str(xlsx)])

    saida = capsys.readouterr().out
    assert rc == 2
    assert "Traceback" not in saida
    assert "NÃO verificado" in saida


def test_tesseract_usa_which_quando_disponivel(monkeypatch):
    from detectores import imagem
    monkeypatch.setattr(imagem.shutil, "which", lambda nome: "/usr/bin/tesseract")
    assert imagem._tesseract() == "/usr/bin/tesseract"


def test_tesseract_cai_para_caminho_fixo_quando_which_nao_encontra(monkeypatch):
    from detectores import imagem
    monkeypatch.setattr(imagem.shutil, "which", lambda nome: None)
    monkeypatch.delenv("ProgramFiles", raising=False)
    monkeypatch.delenv("ProgramFiles(x86)", raising=False)
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\fulano\AppData\Local")
    caminho_esperado = os.path.join(r"C:\Users\fulano\AppData\Local", "Programs", "Tesseract-OCR", "tesseract.exe")

    def fake_isfile(caminho):
        return caminho == caminho_esperado

    monkeypatch.setattr(imagem.os.path, "isfile", fake_isfile)

    assert imagem._tesseract() == caminho_esperado


def test_tesseract_retorna_none_quando_nada_encontrado(monkeypatch):
    from detectores import imagem
    monkeypatch.setattr(imagem.shutil, "which", lambda nome: None)
    monkeypatch.setattr(imagem.os.path, "isfile", lambda caminho: False)
    assert imagem._tesseract() is None
