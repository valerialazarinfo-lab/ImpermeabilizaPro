#!/usr/bin/env python3
"""Verificação estática do site. Uso: python3 scripts/verificar_site.py  (sai com erro se algo falhar)."""
import json, pathlib, re, subprocess, sys, urllib.parse

RAIZ = pathlib.Path(__file__).resolve().parent.parent
erros, avisos = [], []
paginas = sorted(p for p in RAIZ.rglob("*.html") if ".git" not in p.parts and "partials" not in p.parts and not p.name.startswith("google"))

for p in paginas:
    rel = p.relative_to(RAIZ)
    s = p.read_text(encoding="utf-8")
    if p.name == "index.html":
        if len(re.findall(r"<h1\b", s)) != 1:
            erros.append(f"{rel}: deve ter exatamente um <h1>")
        if not re.search(r"<title>[^<]{10,}</title>", s):
            erros.append(f"{rel}: sem <title>")
        if 'rel="canonical"' not in s and "noindex" not in s:
            erros.append(f"{rel}: sem canonical")
    ids = re.findall(r'\sid="([^"]+)"', s)
    for d in {i for i in ids if ids.count(i) > 1}:
        erros.append(f"{rel}: id duplicado «{d}»")
    for bloco in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', s, re.S):
        try:
            json.loads(bloco)
        except ValueError as e:
            erros.append(f"{rel}: JSON-LD inválido ({e})")
    for url in re.findall(r'(?:href|src)="([^"]+)"', s) + [u.split()[0] for ss in re.findall(r'srcset="([^"]+)"', s) for u in ss.split(",")]:
        if url.startswith(("http", "mailto:", "tel:", "#", "data:", "javascript:")):
            continue
        caminho = urllib.parse.urlparse(url).path
        alvo = (RAIZ / caminho.lstrip("/")) if caminho.startswith("/") else (p.parent / caminho)
        if caminho.endswith("/") or alvo.is_dir():
            alvo = alvo / "index.html"
        if not alvo.exists():
            erros.append(f"{rel}: ligação/recurso inexistente {url}")
    for img in re.findall(r"<img\b[^>]*>", s):
        if "alt=" not in img:
            erros.append(f"{rel}: imagem sem alt: {img[:80]}")

sitemap = (RAIZ / "sitemap.xml").read_text(encoding="utf-8")
for loc in re.findall(r"<loc>https://impermeabilizapro\.pt/([^<]*)</loc>", sitemap):
    if not (RAIZ / loc / "index.html").exists():
        erros.append(f"sitemap: {loc} não existe")

for cmd in (["python3", "scripts/definir_minimo_obra.py", "--verificar"],
            ["python3", "scripts/harmonizar_layout.py", "--verificar"],
            ["node", "--test", "calculadora/motor.test.mjs"],
            ["node", "--check", "script.js"]):
    r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True)
    if r.returncode:
        erros.append(" ".join(cmd) + " falhou:\n" + (r.stdout + r.stderr)[-1500:])

print(f"{len(paginas)} páginas verificadas.")
if erros:
    print("ERROS:\n- " + "\n- ".join(erros))
    sys.exit(1)
print("OK: sem erros.")
