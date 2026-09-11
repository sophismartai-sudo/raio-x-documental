# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
import zipfile
from lxml import etree
from achados import Achado, SEV_MEDIO
from severidade import para
from padroes_injecao import casar_injecao
from normalizacao import varrer_caracteres, normalizar
from xml_seguro import parse_xml, declaracao_doctype

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
FONTE_MIN_MEIOPT = 4          # w:sz é em meios-pontos; 4 = 2pt
BRANCOS = {"FFFFFF", "FEFEFE", "FDFDFD"}

def _texto_run(r) -> str:
    return "".join(t.text or "" for t in r.iter(f"{W}t"))

def _fundo_colorido(r) -> bool:
    node = r
    while node is not None:
        for props_tag in (f"{W}rPr", f"{W}pPr", f"{W}tcPr"):
            props = node.find(props_tag)
            if props is not None:
                shd = props.find(f"{W}shd")
                if shd is not None:
                    fill = (shd.get(f"{W}fill") or "").upper()
                    if fill and fill not in ("AUTO", "FFFFFF", "FEFEFE", "FDFDFD"):
                        return True
        node = node.getparent()
    return False

def analisar_docx(caminho: str) -> list[Achado]:
    achados: list[Achado] = []
    texto_total: list[str] = []
    with zipfile.ZipFile(caminho) as z:
        partes = [n for n in z.namelist() if n.startswith("word/") and n.endswith(".xml")]
        for parte in partes:
            dados = z.read(parte)
            dt = declaracao_doctype(dados)
            if dt is not None:
                injecao_dt = bool(casar_injecao(normalizar(dt)))
                achados.append(Achado(tecnica="entidade_xml", severidade=para("entidade_xml", injecao_dt),
                                      local=parte, trecho=dt))
            try:
                root = parse_xml(dados)
            except etree.XMLSyntaxError as e:
                erro = str(e).splitlines()[0][:200]
                achados.append(Achado(tecnica="nao_verificado", severidade=SEV_MEDIO, local=parte,
                                      trecho=f"parte XML ilegível — NÃO verificada ({erro})"))
                continue
            for r in root.iter(f"{W}r"):
                txt = _texto_run(r)
                if txt:
                    texto_total.append(txt)
                if not txt.strip():
                    continue
                rpr = r.find(f"{W}rPr")
                tecnica = None
                if rpr is not None:
                    if rpr.find(f"{W}vanish") is not None:
                        tecnica = "texto_oculto"
                    else:
                        cor = rpr.find(f"{W}color")
                        sz = rpr.find(f"{W}sz")
                        if cor is not None and (cor.get(f"{W}val") or "").upper() in BRANCOS and not _fundo_colorido(r):
                            tecnica = "branco_no_branco"
                        elif sz is not None:
                            try:
                                if int(sz.get(f"{W}val")) < FONTE_MIN_MEIOPT:
                                    tecnica = "fonte_minuscula"
                            except (TypeError, ValueError):
                                pass
                if tecnica:
                    injecao = bool(casar_injecao(normalizar(txt)))
                    achados.append(Achado(tecnica=tecnica, severidade=para(tecnica, injecao),
                                          local=parte, trecho=txt.strip()))
    achados.extend(varrer_caracteres("".join(texto_total), local="documento"))
    return achados
