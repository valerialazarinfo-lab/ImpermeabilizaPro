#!/usr/bin/env python3
"""Mínimo de obra do site. Fonte única: calculadora/precos.csv (linha config;minimo_obra_m2).

Uso:
  python3 scripts/definir_minimo_obra.py 200          # muda para 200 m² em todo o site
  python3 scripts/definir_minimo_obra.py --verificar  # falha se alguma página estiver desalinhada

O script grava o valor no CSV e atualiza, em todos os HTML:
  - <span data-minimo-obra>N</span>
  - frases «a partir de N m²» e «mínimo de obra é/de N m²» (metadados e dados estruturados)
"""
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CSV = RAIZ / "calculadora" / "precos.csv"
LINHA = re.compile(r"^(config;minimo_obra_m2;[^;]*;)(\d+)(;)(\d+)(;.*)$", re.M)
PADROES = [
    re.compile(r"(<span data-minimo-obra>)(\d+)(</span>)"),
    re.compile(r"((?:[Aa] partir de|[Mm]ínimo de obra(?: é| de)?) )(\d+)( m²)"),
]


def valor_atual():
    m = LINHA.search(CSV.read_text(encoding="utf-8"))
    if not m:
        sys.exit("Não encontrei a linha config;minimo_obra_m2 em calculadora/precos.csv")
    return int(m.group(2))


def paginas():
    return sorted(p for p in RAIZ.rglob("*.html") if ".git" not in p.parts)


def verificar():
    n = valor_atual()
    erros = []
    for p in paginas():
        t = p.read_text(encoding="utf-8")
        for rx in PADROES:
            for m in rx.finditer(t):
                if int(m.group(2)) != n:
                    erros.append(f"{p.relative_to(RAIZ)}: «{m.group(0)}» (esperado {n})")
    if erros:
        sys.exit("Mínimo desalinhado:\n" + "\n".join(erros))
    print(f"OK: mínimo de obra = {n} m² em todas as páginas.")


def definir(novo):
    if not 1 <= novo <= 5000:
        sys.exit("Valor fora do intervalo 1–5000 m².")
    texto = CSV.read_text(encoding="utf-8")
    CSV.write_text(LINHA.sub(lambda m: f"{m.group(1)}{novo}{m.group(3)}{novo}{m.group(5)}", texto), encoding="utf-8")
    alteradas = 0
    for p in paginas():
        t = p.read_text(encoding="utf-8")
        t2 = t
        for rx in PADROES:
            t2 = rx.sub(lambda m: f"{m.group(1)}{novo}{m.group(3)}", t2)
        if t2 != t:
            p.write_text(t2, encoding="utf-8")
            alteradas += 1
    print(f"Mínimo de obra = {novo} m² ({alteradas} páginas atualizadas).")
    print("Lembrete: atualize o ?v= de precos.csv em calculadora/index.html para limpar a cache dos visitantes.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--verificar":
        verificar()
    else:
        definir(int(sys.argv[1]))
