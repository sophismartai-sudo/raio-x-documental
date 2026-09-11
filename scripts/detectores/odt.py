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

STYLE = "urn:oasis:names:tc:opendocument:xmlns:style:1.0"
TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
FO = "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
BRANCOS = {"#FFFFFF", "#FEFEFE", "#FDFDFD"}

def _mapa_estilos(root) -> dict:
    estilos = {}
    for st in root.iter(f"{{{STYLE}}}style"):
        nome = st.get(f"{{{STYLE}}}name")
        props = st.find(f"{{{STYLE}}}text-properties")
        if nome and props is not None:
            estilos[nome] = {
                "cor": (props.get(f"{{{FO}}}color") or "").upper(),
                "fundo": (props.get(f"{{{FO}}}background-color") or "").upper(),
                "tam": props.get(f"{{{FO}}}font-size") or "",
                "oculto": props.get(f"{{{TEXT}}}display") == "none",
            }
    return estilos

def _tam_pt(v: str) -> float:
    try:
        return float(v.replace("pt", "").replace("cm", "").strip()) if v else 99.0
    except ValueError:
        return 99.0

def analisar_odt(caminho: str) -> list[Achado]:
    achados: list[Achado] = []
    with zipfile.ZipFile(caminho) as z:
        try:
            dados = z.read("content.xml")
        except KeyError:
            achados.append(Achado(tecnica="nao_verificado", severidade=SEV_MEDIO, local="content.xml",
                                  trecho="content.xml ausente — documento NÃO verificado"))
            return achados
        dt = declaracao_doctype(dados)
        if dt is not None:
            injecao_dt = bool(casar_injecao(normalizar(dt)))
            achados.append(Achado(tecnica="entidade_xml", severidade=para("entidade_xml", injecao_dt),
                                  local="content.xml", trecho=dt))
        try:
            root = parse_xml(dados)
        except etree.XMLSyntaxError as e:
            erro = str(e).splitlines()[0][:200]
            achados.append(Achado(tecnica="nao_verificado", severidade=SEV_MEDIO, local="content.xml",
                                  trecho=f"parte XML ilegível — NÃO verificada ({erro})"))
            return achados
    estilos = _mapa_estilos(root)
    texto_total: list[str] = []
    for span in root.iter(f"{{{TEXT}}}span"):
        txt = "".join(span.itertext())
        if txt:
            texto_total.append(txt)
        if not txt.strip():
            continue
        est = estilos.get(span.get(f"{{{TEXT}}}style-name", ""), {})
        tecnica = None
        if est.get("oculto"):
            tecnica = "texto_oculto"
        elif est.get("cor") in BRANCOS and est.get("fundo", "") in ("", "TRANSPARENT", "#FFFFFF", "#FEFEFE", "#FDFDFD"):
            tecnica = "branco_no_branco"
        elif est.get("tam") and _tam_pt(est["tam"]) < 2.0:
            tecnica = "fonte_minuscula"
        if tecnica:
            injecao = bool(casar_injecao(normalizar(txt)))
            achados.append(Achado(tecnica=tecnica, severidade=para(tecnica, injecao),
                                  local="content.xml", trecho=txt.strip()))
    for p in root.iter(f"{{{TEXT}}}p"):
        texto_total.append("".join(p.itertext()))
    achados.extend(varrer_caracteres("".join(texto_total), local="documento"))
    return achados
