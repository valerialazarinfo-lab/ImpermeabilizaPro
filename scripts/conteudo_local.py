#!/usr/bin/env python3
"""Secção de conteúdo próprio para cada página de localidade (evita páginas quase iguais).
Conteúdo factual: freguesias (divisão administrativa de 2013), fatores gerais da zona e ligação à calculadora.
Não contém obras, avaliações nem números inventados. Uso: python3 scripts/conteudo_local.py
"""
import html, json, pathlib, re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
MIN = re.search(r"^config;minimo_obra_m2;[^;]*;(\d+);", (RAIZ / "calculadora/precos.csv").read_text(encoding="utf-8"), re.M).group(1)
LOCAIS = {
    "mafra": {
        "nome": "Mafra",
        "freguesias": ["Azueira e Sobral da Abelheira", "Carvoeira", "Encarnação", "Enxara do Bispo, Gradil e Vila Franca do Rosário", "Ericeira", "Igreja Nova e Cheleiros", "Mafra", "Malveira e São Miguel de Alcainça", "Milharado", "Santo Isidoro", "Venda do Pinheiro e Santo Estêvão das Galés"],
        "fatores": [
            ("Perto do mar", "Na Ericeira e na faixa costeira, o vento e a maresia desgastam mais depressa as telas expostas, os remates metálicos e as juntas. Um acabamento com proteção UV ou mineral ajuda a durar mais."),
            ("Moradias com terraços", "Muitas casas têm terraços sobre divisões habitadas. Os pontos críticos são os ralos, as soleiras das portas e o encontro com muretes."),
        ],
        "nota_obra": "Uma das obras que mostramos é na Ericeira, concelho de Mafra: um terraço de cobertura com cerca de 200 m².",
    },
    "torres-vedras": {
        "nome": "Torres Vedras",
        "freguesias": ["A dos Cunhados e Maceira", "Campelos e Outeiro da Cabeça", "Carvoeira e Carmões", "Dois Portos e Runa", "Freiria", "Maxial e Monte Redondo", "Ponte do Rol", "Ramalhal", "Santa Maria, São Pedro e Matacães", "São Pedro da Cadeira", "Silveira", "Turcifal", "Ventosa"],
        "fatores": [
            ("Chuva com vento", "No Oeste, a chuva vem muitas vezes batida pelo vento. Entra sobretudo por remates, platibandas, soleiras e juntas, e menos pelo meio da superfície."),
            ("Moradias, armazéns e anexos", "Coberturas planas de armazéns e anexos costumam ter áreas grandes: aí o preço por m² tende a ser mais baixo do que num terraço pequeno."),
        ],
        "nota_obra": "",
    },
    "loures": {
        "nome": "Loures",
        "freguesias": ["Bucelas", "Camarate, Unhos e Apelação", "Fanhões", "Loures", "Lousa", "Moscavide e Portela", "Sacavém e Prior Velho", "Santa Iria de Azoia, São João da Talha e Bobadela", "Santo Antão e São Julião do Tojal", "Santo António dos Cavaleiros e Frielas"],
        "fatores": [
            ("Prédios e condomínios", "Em Sacavém, Moscavide, Portela ou Santo António dos Cavaleiros há muitos terraços de cobertura de prédios. O acesso (elevador ou só escadas) influencia o preço, e a obra costuma precisar de aprovação do condomínio."),
            ("Moradias no interior do concelho", "Em Bucelas, Lousa ou Fanhões são comuns moradias com terraços, anexos e paredes enterradas, onde a humidade vem muitas vezes do terreno."),
        ],
        "nota_obra": "",
    },
    "sintra": {
        "nome": "Sintra",
        "freguesias": ["Agualva e Mira-Sintra", "Algueirão-Mem Martins", "Almargem do Bispo, Pêro Pinheiro e Montelavar", "Cacém e São Marcos", "Casal de Cambra", "Colares", "Massamá e Monte Abraão", "Queluz e Belas", "Rio de Mouro", "São João das Lampas e Terrugem", "Sintra (Santa Maria e São Miguel, São Martinho e São Pedro de Penaferrim)"],
        "fatores": [
            ("Humidade e nevoeiro", "Perto da serra e no litoral, as superfícies demoram mais a secar. A aplicação tem de ser marcada para dias secos, e o suporte tem de estar seco antes de impermeabilizar."),
            ("Caves e paredes enterradas", "Em terrenos inclinados, muitas casas têm caves e paredes encostadas à terra, onde a água entra por pressão do terreno."),
        ],
        "nota_obra": "",
    },
    "lisboa": {
        "nome": "Lisboa",
        "freguesias": [],
        "fatores": [
            ("Edifícios antigos e terraços de cobertura", "Muitos prédios têm terraços sobre habitações, com várias camadas de reparações antigas. Muitas vezes é preciso remover o sistema antigo antes de impermeabilizar."),
            ("Logística na cidade", "Acesso, estacionamento e, quando há contentor ou andaime na rua, a autorização da câmara para ocupar a via pública fazem parte do planeamento da obra."),
        ],
        "nota_obra": "",
    },
}


def bloco(chave, d):
    n = d["nome"]
    h = html.escape
    fatores = "".join(f"<article><h3>{h(t)}</h3><p>{h(x)}</p></article>" for t, x in d["fatores"])
    freg = ""
    if d["freguesias"]:
        freg = f'<p><strong>Freguesias do concelho de {h(n)}:</strong> {h("; ".join(d["freguesias"]))}.</p>'
    else:
        freg = "<p><strong>Toda a cidade de Lisboa</strong>, sujeito a confirmação do acesso e das condições da obra.</p>"
    nota = f"<p>{h(d['nota_obra'])}</p>" if d["nota_obra"] else ""
    faq = [
        (f"Fazem obras de impermeabilização em {n}?", f"Sim. Trabalhamos a partir de Sobral de Monte Agraço e avaliamos obras em {n}. Confirmamos a deslocação com a localidade e fotografias."),
        (f"Quanto custa impermeabilizar em {n}?", "Depende da superfície, do material, do estado do suporte, dos acessos e dos remates. A calculadora do site dá um intervalo por m² e o total com IVA; o valor final é confirmado após avaliação."),
        ("Há um mínimo de obra?", f"Sim, fazemos obras a partir de {MIN} m². Se tiver várias zonas na mesma morada, as áreas somam-se."),
    ]
    faq_html = "".join(f"<details><summary>{h(q)}</summary><p>{h(a).replace(f'{MIN} m²', f'<span data-minimo-obra>{MIN}</span> m²')}</p></details>" for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    return (f'<!-- conteudo-local:inicio -->\n<section class="section" id="zona"><div class="wrap">'
            f'<div class="section-head"><p class="eyebrow">IMPERMEABILIZAÇÃO EM {h(n.upper())}</p><h2>O que muda numa obra em {h(n)}.</h2></div>'
            f'<div class="service-grid">{fatores}</div>{freg}{nota}'
            f'<p><a class="btn whatsapp" href="/calculadora/">Calcular o preço da minha obra</a></p></div></section>\n'
            f'<section class="section faq-section"><div class="wrap narrow"><div class="section-head"><p class="eyebrow">DÚVIDAS FREQUENTES</p><h2>Impermeabilização em {h(n)}: perguntas comuns.</h2></div>{faq_html}</div></section>\n'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n<!-- conteudo-local:fim -->')


for chave, d in LOCAIS.items():
    p = RAIZ / f"impermeabilizacao-{chave}" / "index.html"
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"<!-- conteudo-local:inicio -->.*?<!-- conteudo-local:fim -->\n?", "", s, flags=re.S)
    i = s.index('<section class="section soft">')
    s = s[:i] + bloco(chave, d) + "\n" + s[i:]
    p.write_text(s, encoding="utf-8")
    print("ok", p.relative_to(RAIZ))
