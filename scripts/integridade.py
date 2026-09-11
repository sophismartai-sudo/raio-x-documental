# raio-x-documental — © 2026 Murilo Ferreira (@agro_muriloferreira) / Sophismart.ai (@sophismart.ai)
# Uso público, não comercial, sem derivações. Proibida venda e alteração. Ver LICENSE / AUTORIA.md.
from __future__ import annotations
import hashlib
import pathlib
from typing import List, Tuple

RAIZ = pathlib.Path(__file__).resolve().parent.parent
MANIFESTO = "INTEGRIDADE.sha256"
INCLUIR_DIRS = ("scripts",)                 # todo .py do núcleo
INCLUIR_ARQS = ("SKILL.md", "LICENSE", "README.md", "AUTORIA.md")
EXCLUIR_PARTES = ("__pycache__",)


def _arquivos_cobertos(raiz: pathlib.Path) -> List[pathlib.Path]:
    out: List[pathlib.Path] = []
    for d in INCLUIR_DIRS:
        for p in sorted((raiz / d).rglob("*.py")):
            if any(x in p.parts for x in EXCLUIR_PARTES):
                continue
            out.append(p)
    for a in INCLUIR_ARQS:
        p = raiz / a
        if p.exists():
            out.append(p)
    return out


def _hash(p: pathlib.Path) -> str:
    # normaliza quebras de linha p/ o hash ser estável entre SOs (evita falso alarme por CRLF)
    dados = p.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(dados).hexdigest()


def gerar(raiz: pathlib.Path = RAIZ) -> str:
    linhas = [f"{_hash(p)}  {p.relative_to(raiz).as_posix()}" for p in _arquivos_cobertos(raiz)]
    conteudo = "\n".join(linhas) + "\n"
    (raiz / MANIFESTO).write_text(conteudo, encoding="utf-8")
    return conteudo


def verificar(raiz: pathlib.Path = RAIZ) -> Tuple[bool, List[str]]:
    manifesto = raiz / MANIFESTO
    if not manifesto.exists():
        return (False, [f"manifesto {MANIFESTO} ausente — não é possível atestar integridade"])
    esperado = {}
    for ln in manifesto.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        h, _, rel = ln.partition("  ")
        esperado[rel] = h
    atuais = {p.relative_to(raiz).as_posix(): _hash(p) for p in _arquivos_cobertos(raiz)}
    problemas: List[str] = []
    for rel, h in esperado.items():
        if rel not in atuais:
            problemas.append(f"ausente: {rel}")
        elif atuais[rel] != h:
            problemas.append(f"ALTERADO: {rel}")
    for rel in atuais:
        if rel not in esperado:
            problemas.append(f"não consta no manifesto (adicionado?): {rel}")
    return (not problemas, problemas)


if __name__ == "__main__":
    import sys
    if "--gerar" in sys.argv:
        gerar()
        print(f"Manifesto {MANIFESTO} gerado.")
    else:
        ok, probs = verificar()
        print("Integridade OK." if ok else "INTEGRIDADE COMPROMETIDA:\n  " + "\n  ".join(probs))
        raise SystemExit(0 if ok else 2)
