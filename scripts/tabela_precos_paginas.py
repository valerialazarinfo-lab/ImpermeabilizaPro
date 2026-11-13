#!/usr/bin/env python3
"""Gera a tabela «Preços de referência» das páginas de preço a partir de calculadora/precos.csv.
Só publica linhas com fonte (as marcadas «HIPÓTESE» ficam de fora). Uso: python3 scripts/tabela_precos_paginas.py
Corra sempre que mudar precos.csv, para as páginas e a calculadora dizerem o mesmo.
"""
import html, pathlib, re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
linhas = [l for l in (RAIZ / "calculadora/precos.csv").read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
cab = linhas[0].split(";")
T = {}
for l in linhas[1:]:
    c = l.split(";", len(cab) - 1)
    r = dict(zip(cab, c))
    T[(r["grupo"], r["chave"])] = r
IVA = float(T[("config", "iva_percentagem")]["min"].replace(",", "."))
MIN = T[("config", "minimo_obra_m2")]["min"]
num = lambda v: float(v.replace(",", "."))
eur = lambda v: f"{v:,.0f}".replace(",", " ")

PAGINAS = {
    ".": [("material", "tela_1"), ("material", "tela_2"), ("material", "membrana_liquida"), ("remocao", "tela_antiga"), ("suporte", "degradado"), ("acesso", "escadas")],
    "impermeabilizacao-terraco-preco": [("material", "tela_1"), ("material", "tela_2"), ("material", "membrana_liquida"),
                                        ("remocao", "tela_antiga"), ("remocao", "sobre_ceramico"), ("suporte", "degradado"), ("suporte", "pendentes"), ("acesso", "escadas")],
    "tela-asfaltica-preco": [("material", "tela_1"), ("material", "tela_2"), ("remocao", "tela_antiga"), ("suporte", "degradado"), ("suporte", "pendentes"), ("acesso", "escadas")],
}
SUP = {"impermeabilizacao-terraco-preco": "terraco", "tela-asfaltica-preco": "cobertura_plana", ".": "cobertura_plana"}


def tabela(chaves):
    rows = []
    for g, k in chaves:
        r = T[(g, k)]
        if "HIPÓTESE" in r["origem"]:
            continue
        a, b = num(r["min"]), num(r["max"])
        tipo = "Preço base" if g == "material" else "Acréscimo"
        sinal = "" if g == "material" else "+ "
        rotulo = {"suporte": "Suporte: ", "acesso": "Acesso: "}.get(g, "") + r["descricao"]
        rows.append(f"<tr><th scope=\"row\">{html.escape(rotulo)}<small>{tipo}</small></th>"
                    f"<td>{sinal}{eur(a)}–{eur(b)} €/m²</td><td>{sinal}{eur(a*(1+IVA/100))}–{eur(b*(1+IVA/100))} €/m²</td></tr>")
    return "".join(rows)


for pag, chaves in PAGINAS.items():
    p = RAIZ / "index.html" if pag == "." else RAIZ / pag / "index.html"
    s = p.read_text(encoding="utf-8")
    marcador = re.search(r"<!-- precos-referencia:inicio -->.*?<!-- precos-referencia:fim -->\n?", s, flags=re.S)
    pos = marcador.start() if marcador else None
    s = re.sub(r"<!-- precos-referencia:inicio -->.*?<!-- precos-referencia:fim -->\n?", "", s, flags=re.S)
    bloco = (f'<!-- precos-referencia:inicio -->\n<section class="section soft h-sec" id="precos"><div class="wrap">'
             f'<div class="section-head"><p class="eyebrow">PREÇOS DE REFERÊNCIA</p><h2>Quanto custa, em €/m².</h2>'
             f'<p>Material e mão de obra, para obras a partir de <span data-minimo-obra>{MIN}</span> m², com acesso fácil. Os acréscimos somam-se ao preço base quando se aplicam.</p></div>'
             f'<div class="price-table-wrap"><table class="price-table"><thead><tr><th scope="col">Trabalho</th><th scope="col">Sem IVA</th><th scope="col">Com IVA ({IVA:.0f}%)</th></tr></thead><tbody>{tabela(chaves)}</tbody></table></div>'
             f'<p class="micro">Valores indicativos, não são um orçamento. Ralos, remates, isolamento, acabamento, urgência e deslocação também contam: a calculadora junta tudo.</p>'
             f'<p><a class="btn whatsapp big" href="/calculadora/?superficie={SUP[pag]}">Calcular o preço da minha obra</a></p>'
             f'</div></section>\n' + ('' if pag == '.' else f'<style>.price-table-wrap{{overflow-x:auto}}.price-table{{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;font-size:.95rem}}.price-table th,.price-table td{{padding:12px 14px;border-bottom:1px solid #e1e8ee;text-align:left;vertical-align:top}}.price-table thead th{{background:#0a2340;color:#fff}}.price-table td{{white-space:nowrap;font-weight:700}}.price-table small{{display:block;color:#5b6d7c;font-weight:400}}</style>\n') + '<!-- precos-referencia:fim -->\n')
    i = pos if pos is not None else s.index('<section class="section">')
    s = s[:i] + bloco + s[i:]
    p.write_text(s, encoding="utf-8")
    print("ok", pag)
