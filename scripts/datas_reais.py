#!/usr/bin/env python3
"""Datas verdadeiras: correr depois de gerar_paginas.py e harmonizar_layout.py.

1. Páginas (e llms.txt) que só mudaram na data («Atualizado em …», dateModified) voltam à versão do último commit:
   não se anuncia uma atualização que não houve.
2. O sitemap.xml recebe, por URL, a data da última alteração real: a de hoje se a página mudou e ainda não está
   no commit, senão a data do último commit que a alterou.
Uso: python3 scripts/datas_reais.py
"""
import datetime
import pathlib
import re
import subprocess

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://impermeabilizapro.pt"
HOJE = datetime.date.today().isoformat()
DATA = re.compile(r"20\d\d-\d\d-\d\d")


def git(*args):
    r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def no_commit(rel):
    return git("show", f"HEAD:{rel}")


def repor_so_datas():
    alterados = (git("diff", "--name-only", "HEAD") or "").split()
    repostos = []
    for rel in alterados:
        if not (rel.endswith(".html") or rel == "llms.txt"):
            continue
        antes, agora = no_commit(rel), (RAIZ / rel).read_text(encoding="utf-8") if (RAIZ / rel).exists() else None
        if antes is None or agora is None:
            continue
        if antes != agora and DATA.sub("D", antes) == DATA.sub("D", agora):
            (RAIZ / rel).write_text(antes, encoding="utf-8")
            repostos.append(rel)
    return repostos


def data_real(rel):
    if not (RAIZ / rel).exists():
        return HOJE
    if no_commit(rel) is None or git("diff", "--quiet", "HEAD", "--", rel) is None:
        return HOJE  # ficheiro novo ou alterado e ainda sem commit
    return (git("log", "-1", "--format=%cs", "--", rel) or HOJE).strip() or HOJE


def sitemap():
    p = RAIZ / "sitemap.xml"
    s = p.read_text(encoding="utf-8")

    def troca(m):
        loc = m.group(1)
        caminho = loc[len(SITE) + 1:]
        rel = (caminho + "index.html") if (caminho == "" or caminho.endswith("/")) else caminho
        return f"<url><loc>{loc}</loc><lastmod>{data_real(rel)}</lastmod></url>"

    p.write_text(re.sub(r"<url><loc>([^<]+)</loc><lastmod>[^<]*</lastmod></url>", troca, s), encoding="utf-8")


if __name__ == "__main__":
    r = repor_so_datas()
    sitemap()
    print(f"{len(r)} ficheiros só com a data mudada foram repostos; sitemap com datas reais.")
