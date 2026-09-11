# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
import re
from lxml import etree

# DOCTYPE completo, incluindo o subconjunto interno "[ ... ]" quando presente
# (é aí que uma entidade externa maliciosa é declarada). re.S para casar quebras
# de linha dentro do subconjunto interno.
_RE_DOCTYPE = re.compile(rb"<!DOCTYPE.*?(?:\[.*?\]\s*)?>", re.S)
_DOCTYPE_MAX_CHARS = 500


def parse_xml(dados: bytes) -> "etree._Element":
    """Parse seguro de partes XML internas de DOCX/ODT.

    Nunca resolve entidades externas nem carrega DTD externa/rede — impede XXE
    (leitura de arquivo local ou acesso de rede via `<!ENTITY x SYSTEM "...">`)
    mesmo em versões do lxml cujo parser padrão resolveria entidades. Também
    limita huge_tree para não abrir a porta a "billion laughs"/entity expansion.
    """
    parser = etree.XMLParser(resolve_entities=False, no_network=True,
                              load_dtd=False, huge_tree=False)
    return etree.fromstring(dados, parser)


def declaracao_doctype(dados: bytes) -> str | None:
    """Texto do DOCTYPE (incl. subconjunto interno), truncado a 500 caracteres.

    None se não houver DOCTYPE. Word e LibreOffice NUNCA emitem DOCTYPE nas
    partes XML internas (word/*.xml, content.xml) — a presença de um é, por si
    só, anômala e é a assinatura do ataque de entidade externa/DOCTYPE.
    """
    m = _RE_DOCTYPE.search(dados)
    if not m:
        return None
    return m.group(0).decode("utf-8", errors="replace")[:_DOCTYPE_MAX_CHARS]
