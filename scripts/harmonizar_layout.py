#!/usr/bin/env python3
"""Aplica o mesmo cabeçalho, rodapé, barra do mínimo de obra, cookies e script.js a todas as páginas.

Fonte única: scripts/partials/header.html e scripts/partials/footer.html.
Uso: python3 scripts/harmonizar_layout.py            (aplica)
     python3 scripts/harmonizar_layout.py --verificar (falha se alguma página estiver diferente)

- O link de WhatsApp do cabeçalho de cada página é mantido (mensagens diferentes por serviço).
- Páginas com layout próprio (simulador) e ficheiros de verificação são ignorados.
"""
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
JS_VERSAO = "20261113-layout1"
WA_PADRAO = ("https://wa.me/351930446198?text=Ol%C3%A1%2C%20gostaria%20de%20pedir%20uma%20avalia%C3%A7%C3%A3o%20para%20uma%20"
             "impermeabiliza%C3%A7%C3%A3o.%20A%20obra%20fica%20em%20%5Blocalidade%5D.%20Posso%20enviar%20fotografias.")
IGNORAR = {"simulador"}
HEADER = (RAIZ / "scripts/partials/header.html").read_text(encoding="utf-8").strip()
FOOTER = (RAIZ / "scripts/partials/footer.html").read_text(encoding="utf-8").strip()

RX_HEADER = re.compile(r'<header class="header">.*?</header>\s*(<div class="min-obra-bar".*?</div>)?', re.S)
RX_FIM = re.compile(r"<footer>.*?(?=</body>)", re.S)


def paginas():
    for p in sorted(RAIZ.glob("**/index.html")):
        rel = p.relative_to(RAIZ)
        if ".git" in rel.parts or (rel.parts[0] in IGNORAR and len(rel.parts) > 1):
            continue
        yield p


def aplicar(texto):
    m = RX_HEADER.search(texto)
    if not m:
        raise ValueError("sem <header class=\"header\">")
    wa = re.search(r'href="(https://wa\.me/[^"]+)"', m.group(0))
    wa = wa.group(1) if wa else WA_PADRAO
    if wa.rstrip("/") == "https://wa.me/351930446198":
        wa = WA_PADRAO
    novo = texto[:m.start()] + HEADER.replace("{{WA}}", wa) + texto[m.end():]
    fim = RX_FIM.search(novo)
    if not fim:  # páginas sem rodapé: acrescenta antes de </body>
        i = novo.rindex("</body>")
        novo = novo[:i] + "<footer></footer>\n" + novo[i:]
        fim = RX_FIM.search(novo)
    rodape = FOOTER.replace("{{WA}}", wa).replace("{{JSV}}", JS_VERSAO)
    # Mantém scripts próprios da página (ex.: calculadora) que estavam depois do rodapé.
    proprios = [s for s in re.findall(r"<script\b(?![^>]*script\.js).*?</script>", fim.group(0), re.S)]
    novo = novo[:fim.start()] + rodape + "\n" + "\n".join(proprios) + ("\n" if proprios else "") + novo[fim.end():]
    return novo


def main():
    verificar = sys.argv[1:] == ["--verificar"]
    diferentes = []
    for p in paginas():
        t = p.read_text(encoding="utf-8")
        n = aplicar(t)
        if n != t:
            diferentes.append(str(p.relative_to(RAIZ)))
            if not verificar:
                p.write_text(n, encoding="utf-8")
    if verificar and diferentes:
        sys.exit("Layout desalinhado em: " + ", ".join(diferentes) + "\nCorra: python3 scripts/harmonizar_layout.py")
    print(("Verificado" if verificar else "Atualizadas") + f": {len(diferentes)} páginas diferentes.")


if __name__ == "__main__":
    main()
