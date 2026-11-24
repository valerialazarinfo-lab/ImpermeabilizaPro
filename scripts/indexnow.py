#!/usr/bin/env python3
"""Avisa os motores IndexNow (Bing, Yandex, Seznam…) das páginas do sitemap que mudaram entre dois commits.

A chave é pública por desenho: o ficheiro <chave>.txt na raiz prova que o site é nosso. Não é um segredo.
Uso: python3 scripts/indexnow.py <commit_antes> <commit_depois> [--simular]
"""
import json
import pathlib
import re
import subprocess
import sys
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://impermeabilizapro.pt"
HOST = "impermeabilizapro.pt"


def chave():
    ks = [p for p in RAIZ.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem) and p.read_text().strip() == p.stem]
    if len(ks) != 1:
        sys.exit("Esperava exatamente um ficheiro de chave IndexNow na raiz.")
    return ks[0].stem


def urls_alteradas(antes, depois):
    if set(antes) == {"0"}:  # primeiro push do ramo: não há «antes»
        nomes = subprocess.run(["git", "ls-files", "*.html"], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.split()
    else:
        nomes = subprocess.run(["git", "diff", "--name-only", antes, depois], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.split()
    no_sitemap = set(re.findall(r"<loc>([^<]+)</loc>", (RAIZ / "sitemap.xml").read_text(encoding="utf-8")))
    urls = []
    for n in nomes:
        if n == "index.html":
            u = SITE + "/"
        elif n.endswith("/index.html"):
            u = f"{SITE}/{n[:-len('index.html')]}"
        else:
            continue
        if u in no_sitemap:
            urls.append(u)
    return sorted(set(urls))


def main():
    antes, depois = sys.argv[1], sys.argv[2]
    k = chave()
    urls = urls_alteradas(antes, depois)
    if not urls:
        print("Nenhuma página do sitemap mudou: nada a enviar.")
        return
    dados = {"host": HOST, "key": k, "keyLocation": f"{SITE}/{k}.txt", "urlList": urls}
    print(f"{len(urls)} URL(s):", *urls, sep="\n  ")
    if "--simular" in sys.argv:
        print("Simulação: nada enviado.")
        return
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=json.dumps(dados).encode(), headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print("IndexNow respondeu", r.status)
    except urllib.error.HTTPError as e:
        sys.exit(f"IndexNow recusou: {e.code} {e.read()[:300]!r}")


if __name__ == "__main__":
    main()
