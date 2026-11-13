#!/usr/bin/env python3
"""SEO build for the static ImpermeabilizaPro website.

Idempotent: run it again after editing pages or business data.
    python3 scripts/seo_build.py

What it does (only with confirmed, public business data defined below):
  * one business entity (@id) shared by every page's JSON-LD, plus WebSite,
    WebPage and BreadcrumbList; Service providers point to that @id;
  * Open Graph tags where missing;
  * a crawlable internal-link hub (services, zones, guides, NAP) on every page;
  * unique local content + FAQ (visible and FAQPage) on the local pages;
  * sitemap.xml and llms.txt generated from the page list.

Never add ratings, prices, guarantees, certifications, opening hours or a
street address here unless the business has confirmed them.
"""
import datetime
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://impermeabilizapro.pt"
BIZ_ID = SITE + "/#negocio"
SITE_ID = SITE + "/#website"
PERSON_ID = SITE + "/#vinicius-nascimento"
MAPS = "https://maps.google.com/maps?cid=17222012943464360492"
PHONE = "+351930446198"
PHONE_TXT = "930 446 198"
EMAIL = "proimpermeabiliza@gmail.com"
TODAY = datetime.date.today().isoformat()

SERVICES = [
    ("/terracos/", "Terraços e varandas", "Impermeabilização de terraços e varandas"),
    ("/coberturas-planas/", "Coberturas planas", "Impermeabilização de coberturas planas"),
    ("/paredes/", "Paredes e paredes enterradas", "Impermeabilização de paredes e paredes enterradas"),
    ("/casas-de-banho/", "Casas de banho e interiores", "Impermeabilização de casas de banho e zonas interiores"),
    ("/tela-asfaltica/", "Tela asfáltica", "Aplicação de tela asfáltica"),
    ("/reparacao-infiltracoes/", "Reparação de infiltrações", "Reparação de infiltrações"),
    ("/empresas/", "Empreiteiros e empresas", "Subcontratação de impermeabilização para empreiteiros"),
]
ZONES = [
    ("/impermeabilizacao-sobral-de-monte-agraco/", "Sobral de Monte Agraço"),
    ("/impermeabilizacao-torres-vedras/", "Torres Vedras"),
    ("/impermeabilizacao-mafra/", "Mafra e Ericeira"),
    ("/impermeabilizacao-loures/", "Loures"),
    ("/impermeabilizacao-lisboa/", "Lisboa"),
    ("/impermeabilizacao-sintra/", "Sintra"),
]
GUIDES = [
    ("/impermeabilizacao-terraco-preco/", "Preço de impermeabilizar um terraço"),
    ("/tela-asfaltica-preco/", "Preço da tela asfáltica"),
    ("/humidade-parede-exterior/", "Humidade na parede exterior"),
    ("/simulador/", "Mapa da Infiltração (orientação inicial)"),
]
# Pages handled by this script (path -> breadcrumb name). Excluded on purpose:
# /telhados/ (noindex, historical URL that refreshes to /coberturas-planas/)
# and the private e-mail signature pages.
PAGES = {"/": "Início"}
PAGES.update({p: n for p, n, _ in SERVICES})
PAGES.update({p: "Impermeabilização em " + n for p, n in ZONES})
PAGES.update({p: n for p, n in GUIDES})
LEGAL = {"/privacidade/": "Privacidade e cookies", "/informacoes-legais/": "Informações legais"}
PAGES.update(LEGAL)

DISTRICTS = ["Lisboa", "Santarém", "Setúbal", "Leiria"]
# Same service area as the Google Business Profile (proimpermeabiliza@gmail.com,
# confirmed 13-11-2026). Keep both lists identical when either changes.
GBP_AREAS = [
    "Sobral de Monte Agraço", "Torres Vedras", "Arruda dos Vinhos", "Alenquer", "Mafra", "Loures",
    "Lisboa", "Sintra", "Odivelas", "Vila Franca de Xira", "Lourinhã", "Cadaval", "Amadora",
]

BUSINESS = {
    "@type": "HomeAndConstructionBusiness",
    "@id": BIZ_ID,
    "name": "ImpermeabilizaPro",
    "url": SITE + "/",
    "logo": {"@type": "ImageObject", "url": SITE + "/assets/logo-impermeabilizapro.webp", "width": 220, "height": 220},
    "image": [
        SITE + "/assets/foto-real-20260915-162914.jpeg",
        SITE + "/assets/caso-ericeira-200m2.webp",
        SITE + "/assets/caso-gaia-440m2.webp",
    ],
    "description": (
        "Profissional de impermeabilização com base em Sobral de Monte Agraço. Impermeabilização de "
        "terraços, varandas, coberturas planas, paredes, paredes enterradas, casas de banho e interiores, "
        "aplicação de tela asfáltica e reparação de infiltrações nos distritos de Lisboa, Santarém, "
        "Setúbal e Leiria. Trabalho completo ou só mão de obra para empreiteiros."
    ),
    "telephone": PHONE,
    "email": EMAIL,
    "address": {
        "@type": "PostalAddress",
        "addressLocality": "Sobral de Monte Agraço",
        "addressRegion": "Lisboa",
        "addressCountry": "PT",
    },
    "hasMap": MAPS,
    "sameAs": [MAPS],
    "areaServed": [{"@type": "AdministrativeArea", "name": "Distrito de " + d} for d in DISTRICTS]
    + [{"@type": "City", "name": n} for n in GBP_AREAS],
    "knowsAbout": [
        "impermeabilização de terraços", "impermeabilização de varandas", "impermeabilização de coberturas planas",
        "impermeabilização de paredes enterradas", "humidade em paredes", "infiltrações", "tela asfáltica",
        "membrana líquida", "impermeabilização de casas de banho",
    ],
    "knowsLanguage": "pt-PT",
    "contactPoint": {
        "@type": "ContactPoint",
        "telephone": PHONE,
        "email": EMAIL,
        "contactType": "orçamentos",
        "availableLanguage": ["Portuguese"],
        "areaServed": "PT",
    },
    "employee": {"@id": PERSON_ID},
    "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "Serviços de impermeabilização",
        "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": full, "url": SITE + p}}
            for p, _, full in SERVICES
        ],
    },
}
PERSON = {
    "@type": "Person",
    "@id": PERSON_ID,
    "name": "Vinícius Nascimento",
    "jobTitle": "Responsável pela ImpermeabilizaPro",
    "image": SITE + "/assets/vinicius-nascimento-v2.webp",
    "worksFor": {"@id": BIZ_ID},
}
WEBSITE = {
    "@type": "WebSite",
    "@id": SITE_ID,
    "url": SITE + "/",
    "name": "ImpermeabilizaPro",
    "inLanguage": "pt-PT",
    "publisher": {"@id": BIZ_ID},
}

# Unique local content. Only geography (parishes/localities) and
# general technical guidance: no invented jobs, numbers or claims.
LOCAL = {
    "/impermeabilizacao-sobral-de-monte-agraco/": {
        "place": "Sobral de Monte Agraço",
        "intro": "É aqui que a ImpermeabilizaPro tem base. Por estarmos perto, é mais simples combinar uma visita para ver a origem de uma infiltração, acompanhar a preparação da base e voltar à obra quando for preciso.",
        "zones": ["Sobral de Monte Agraço", "Sapataria", "Santo Quintino", "Pero Negro", "Arruda dos Vinhos", "Alenquer", "Torres Vedras", "Mafra"],
        "context": "Em moradias, os terraços sobre divisões habitadas, as paredes enterradas e os muros são pontos onde a humidade aparece com frequência. Antes de propor uma solução, verificamos o estado da base, os ralos, os remates junto a muretes e soleiras e a forma como a água escoa.",
        "faq": [
            ("Fazem visitas em Sobral de Monte Agraço?", "Sim. Como temos base no concelho, a visita para avaliar a obra é normalmente mais fácil de combinar. Pode começar por enviar fotografias pelo WhatsApp."),
            ("Também trabalham em Arruda dos Vinhos, Alenquer e Torres Vedras?", "Sim, avaliamos pedidos nos concelhos vizinhos e nos distritos de Lisboa, Santarém, Setúbal e Leiria, sujeitos à confirmação da localidade."),
            ("Fazem só a mão de obra?", "Sim. Podemos executar o trabalho completo, com materiais, ou apenas a mão de obra quando o cliente ou o empreiteiro já tem o material."),
        ],
    },
    "/impermeabilizacao-torres-vedras/": {
        "place": "Torres Vedras",
        "intro": "Torres Vedras fica junto ao concelho onde temos base (Sobral de Monte Agraço), o que facilita combinar visitas e acompanhar a obra.",
        "zones": ["Torres Vedras (cidade)", "Silveira", "Santa Cruz", "Ponte do Rol", "A dos Cunhados", "Maceira", "Ramalhal", "Campelos", "Turcifal", "Dois Portos", "Runa", "São Pedro da Cadeira", "Ventosa", "Maxial"],
        "context": "Nas zonas mais perto do mar, como Santa Cruz e Silveira, a exposição ao vento e à humidade deve pesar na escolha do sistema e dos remates. Em moradias, os terraços, os muros e as paredes enterradas são os pontos que mais convém verificar.",
        "faq": [
            ("Trabalham em Santa Cruz e na Silveira?", "Sim. Avaliamos pedidos em todo o concelho de Torres Vedras, incluindo as freguesias junto à costa."),
            ("Quanto custa impermeabilizar um terraço em Torres Vedras?", "Depende da área, do estado da base, dos remates, dos acessos e do sistema necessário. Envie fotografias e a área aproximada para uma primeira avaliação sem compromisso."),
            ("Fazem impermeabilização de paredes enterradas?", "Sim, quando há acesso à face exterior da parede ou durante a obra. Avaliamos primeiro a origem da humidade."),
        ],
    },
    "/impermeabilizacao-mafra/": {
        "place": "Mafra",
        "intro": "Trabalhamos no concelho de Mafra, incluindo a Ericeira, onde executámos a impermeabilização de um terraço de cobertura com cerca de 200 m² (fotografia nesta página).",
        "zones": ["Mafra (vila)", "Ericeira", "Malveira", "Venda do Pinheiro", "Milharado", "Santo Isidoro", "Carvoeira", "Encarnação", "Igreja Nova", "Azueira", "Gradil", "Enxara do Bispo", "Cheleiros"],
        "context": "Na Ericeira e nas freguesias junto à costa, o vento, a maresia e a exposição solar desgastam mais depressa as camadas de proteção. Por isso olhamos com atenção para o acabamento, os remates e a drenagem do terraço.",
        "faq": [
            ("Fazem impermeabilização na Ericeira?", "Sim. Já executámos na Ericeira a impermeabilização de um terraço de cobertura com tela e acabamento mineral, e avaliamos novos pedidos em toda a zona."),
            ("Trabalham na Malveira e na Venda do Pinheiro?", "Sim, avaliamos pedidos em todo o concelho de Mafra, sujeitos à confirmação da localidade."),
            ("Que informação devo enviar?", "Fotografias da zona com infiltração ou da superfície a impermeabilizar, a localidade e, se souber, a área aproximada."),
        ],
    },
    "/impermeabilizacao-loures/": {
        "place": "Loures",
        "intro": "Avaliamos pedidos em todo o concelho de Loures, desde a zona urbana junto a Lisboa até às freguesias mais rurais do norte do concelho.",
        "zones": ["Loures (cidade)", "Sacavém", "Moscavide", "Portela", "Santa Iria de Azóia", "Bobadela", "São João da Talha", "Camarate", "Santo António dos Cavaleiros", "Frielas", "Bucelas", "Fanhões", "Lousa", "Santo Antão do Tojal"],
        "context": "Em prédios e moradias mais antigas é comum a infiltração vir de remates degradados, ralos ou juntas, e não da superfície toda. Identificar a origem evita refazer o terraço inteiro quando não é necessário.",
        "faq": [
            ("Trabalham em Sacavém, Moscavide e Portela?", "Sim, avaliamos pedidos em todas as freguesias do concelho de Loures."),
            ("Fazem trabalhos para condomínios?", "Sim. Podemos avaliar terraços, coberturas planas e paredes de condomínios e preparar orçamento para a administração."),
            ("Fazem só reparação de infiltrações?", "Sim. Quando a origem está localizada, a reparação pode ser parcial. A avaliação diz se basta reparar ou se é preciso renovar o sistema."),
        ],
    },
    "/impermeabilizacao-lisboa/": {
        "place": "Lisboa",
        "intro": "Avaliamos pedidos em toda a cidade de Lisboa, em moradias, prédios e condomínios. Em prédios, o acesso ao terraço ou à cobertura é um dos fatores que mais pesam no planeamento.",
        "zones": ["Lumiar", "Benfica", "Alvalade", "Olivais", "Parque das Nações", "Belém", "Campo de Ourique", "Arroios", "Areeiro", "Estrela", "Ajuda", "Alcântara", "Carnide", "Avenidas Novas", "Penha de França", "Marvila"],
        "context": "Em edifícios antigos são frequentes os terraços com várias camadas sobrepostas e remates degradados junto a platibandas, ralos e caixilharias. Avaliamos o suporte antes de decidir se a impermeabilização existente pode ser aproveitada.",
        "faq": [
            ("Trabalham em prédios e condomínios em Lisboa?", "Sim. Avaliamos terraços, coberturas planas e paredes de prédios e preparamos orçamento para a administração do condomínio."),
            ("É preciso estar em casa para a avaliação?", "Para a primeira avaliação basta enviar fotografias pelo WhatsApp. Se for necessária visita, combinamos o acesso consigo."),
            ("Fazem trabalhos em telhados de telha?", "Não. Trabalhamos em terraços, varandas, coberturas planas, paredes e interiores. Não executamos trabalhos em telhados de telha ou inclinados."),
        ],
    },
    "/impermeabilizacao-sintra/": {
        "place": "Sintra",
        "intro": "Avaliamos pedidos no concelho de Sintra, tanto na zona urbana (Cacém, Queluz, Rio de Mouro, Algueirão-Mem Martins) como nas freguesias mais rurais.",
        "zones": ["Sintra (vila)", "Agualva-Cacém", "Queluz", "Massamá", "Monte Abraão", "Rio de Mouro", "Algueirão-Mem Martins", "Belas", "Casal de Cambra", "Almargem do Bispo", "Pêro Pinheiro", "Terrugem", "São João das Lampas", "Colares"],
        "context": "Na serra e nas zonas mais húmidas do concelho, paredes e muros ficam muito tempo molhados. Antes de impermeabilizar, distinguimos entre infiltração, humidade ascensional e condensação, porque a solução é diferente em cada caso.",
        "faq": [
            ("Trabalham em Queluz, Cacém e Rio de Mouro?", "Sim, avaliamos pedidos em todo o concelho de Sintra, sujeitos à confirmação da localidade."),
            ("Tenho humidade numa parede. É infiltração?", "Nem sempre. Pode ser infiltração, humidade que sobe do terreno ou condensação. Envie fotografias da parede por dentro e por fora para uma primeira avaliação."),
            ("Fazem impermeabilização de varandas?", "Sim, incluindo os remates junto a soleiras, guardas e ralos, que são pontos frequentes de entrada de água."),
        ],
    },
}

LD_RE = re.compile(r'<script type="application/ld\+json"([^>]*)>(.*?)</script>\s*', re.S)


def attr(s, pattern):
    m = re.search(pattern, s, re.S)
    return html.unescape(m.group(1).strip()) if m else ""


def meta_description(s):
    return attr(s, r'<meta\s+content="([^"]*)"\s+name="description"') or attr(
        s, r'<meta\s+name="description"\s+content="([^"]*)"'
    )


def walk_provider(node):
    """Point every inline business provider/publisher to the shared @id."""
    if isinstance(node, dict):
        for k, v in list(node.items()):
            if k in ("provider", "publisher") and isinstance(v, dict) and v.get("name") == "ImpermeabilizaPro":
                node[k] = {"@id": BIZ_ID}
            else:
                walk_provider(v)
    elif isinstance(node, list):
        for v in node:
            walk_provider(v)


def process_jsonld(s, path, title, desc):
    has_breadcrumb = False
    out = []

    def repl(m):
        nonlocal has_breadcrumb
        attrs, body = m.group(1), m.group(2)
        if "data-seo-entity" in attrs:
            return ""  # regenerated below
        data = json.loads(body)
        items = data.get("@graph", [data])
        items = [i for i in items if i.get("@type") not in ("HomeAndConstructionBusiness", "LocalBusiness")]
        if not items:
            return ""
        walk_provider(items)
        if any(i.get("@type") == "BreadcrumbList" for i in items):
            has_breadcrumb = True
        if "data-seo-local-faq" in attrs:
            return ""  # regenerated below
        doc = {"@context": "https://schema.org", "@graph": items} if len(items) > 1 else {"@context": "https://schema.org", **items[0]}
        return f'<script type="application/ld+json"{attrs}>{json.dumps(doc, ensure_ascii=False, separators=(",", ":"))}</script>\n'

    s = LD_RE.sub(repl, s)
    url = SITE + path
    graph = [BUSINESS, PERSON, WEBSITE]
    page = {
        "@type": "WebPage",
        "@id": url + "#webpage",
        "url": url,
        "name": title,
        "description": desc,
        "inLanguage": "pt-PT",
        "isPartOf": {"@id": SITE_ID},
        "about": {"@id": BIZ_ID},
    }
    if path != "/" and not has_breadcrumb:
        page["breadcrumb"] = {"@id": url + "#breadcrumb"}
        graph.append({
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Início", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": PAGES[path], "item": url},
            ],
        })
    graph.insert(3, page)
    block = '<script type="application/ld+json" data-seo-entity>' + json.dumps(
        {"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")
    ) + "</script>\n"
    if path in LOCAL:
        faq = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in LOCAL[path]["faq"]
            ],
        }
        block += '<script type="application/ld+json" data-seo-local-faq>' + json.dumps(
            faq, ensure_ascii=False, separators=(",", ":")
        ) + "</script>\n"
    return s.replace("</head>", block + "</head>", 1)


def ensure_og(s, path, title, desc):
    if 'property="og:title"' in s:
        return s
    img = attr(s, r'<img[^>]+src="(/assets/[^"]+)"') or "/assets/foto-real-20260915-162914.jpeg"
    tags = (
        f'<meta property="og:type" content="website">\n<meta property="og:locale" content="pt_PT">\n'
        f'<meta property="og:site_name" content="ImpermeabilizaPro">\n'
        f'<meta property="og:url" content="{SITE}{path}">\n'
        f'<meta property="og:title" content="{html.escape(title)}">\n'
        f'<meta property="og:description" content="{html.escape(desc)}">\n'
        f'<meta property="og:image" content="{SITE}{img}">\n<meta name="twitter:card" content="summary_large_image">\n'
    )
    return s.replace("</head>", tags + "</head>", 1)


def link_list(items, current):
    out = []
    for p, n in items:
        if p == current:
            out.append(f'<li><span aria-current="page">{html.escape(n)}</span></li>')
        else:
            out.append(f'<li><a href="{p}">{html.escape(n)}</a></li>')
    return "".join(out)


def hub(path, with_legal):
    services = [(p, n) for p, n, _ in SERVICES]
    legal = ""
    if with_legal:
        legal = (
            '<p class="seo-hub-legal"><a href="/privacidade/">Política de privacidade</a> · '
            '<a href="/privacidade/#cookies">Cookies</a> · <a href="/informacoes-legais/">Informações legais</a> · '
            '<a href="https://www.livroreclamacoes.pt/Inicio/" target="_blank" rel="noopener noreferrer">Livro de Reclamações</a> · '
            f"© {datetime.date.today().year} ImpermeabilizaPro</p>"
        )
    return (
        "<!-- seo:hub:start -->\n"
        '<section class="seo-hub" aria-label="Serviços, zonas e contactos"><div class="wrap">'
        '<div class="seo-hub-grid">'
        f'<nav aria-label="Serviços"><h2>Serviços</h2><ul>{link_list(services, path)}</ul></nav>'
        f'<nav aria-label="Zonas"><h2>Zonas onde trabalhamos</h2><ul>{link_list(ZONES, path)}</ul></nav>'
        f'<nav aria-label="Guias"><h2>Guias e orçamento</h2><ul>{link_list(GUIDES, path)}</ul></nav>'
        '<div class="seo-hub-nap"><h2>Contacto</h2>'
        '<p><b>ImpermeabilizaPro</b><br>Vinícius Nascimento<br>Base: Sobral de Monte Agraço<br>'
        "Distritos de Lisboa, Santarém, Setúbal e Leiria</p>"
        f'<p><a href="tel:{PHONE}">{PHONE_TXT}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a><br>'
        f'<a href="{MAPS}" target="_blank" rel="noopener noreferrer">Ver no Google Maps</a></p></div>'
        f"</div>{legal}</div></section>\n<!-- seo:hub:end -->\n"
    )


def local_section(path):
    d = LOCAL[path]
    zones = ", ".join(d["zones"][:-1]) + " e " + d["zones"][-1]
    faq = "".join(
        f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in d["faq"]
    )
    return (
        "<!-- seo:local:start -->\n"
        '<section class="section seo-local"><div class="wrap narrow">'
        f'<p class="eyebrow">ZONAS EM {html.escape(d["place"].upper())}</p>'
        f'<h2>Onde trabalhamos em {html.escape(d["place"])}</h2>'
        f'<p>{html.escape(d["intro"])}</p>'
        f'<p>Avaliamos pedidos em {html.escape(zones)}, sujeitos à confirmação da localidade.</p>'
        f'<p>{html.escape(d["context"])}</p>'
        f'<h2>Perguntas frequentes em {html.escape(d["place"])}</h2>{faq}'
        "</div></section>\n<!-- seo:local:end -->\n"
    )


def process(path):
    f = ROOT / path.strip("/") / "index.html" if path != "/" else ROOT / "index.html"
    s = f.read_text(encoding="utf-8")
    title = attr(s, r"<title>(.*?)</title>")
    desc = meta_description(s)
    s = ensure_og(s, path, title, desc)
    if 'rel="canonical"' not in s:
        s = s.replace("</head>", f'<link rel="canonical" href="{SITE}{path}">\n</head>', 1)
    if "/seo-hub.css" not in s:
        s = s.replace("</head>", '<link rel="stylesheet" href="/seo-hub.css?v=20261113-1">\n</head>', 1)
    s = process_jsonld(s, path, title, desc)  # last: keeps the block right before </head>
    s = re.sub(r"<!-- seo:(hub|local):start -->.*?<!-- seo:\1:end -->\n?", "", s, flags=re.S)
    if path in LOCAL:
        s = re.sub(
            r'<p class="nearby">.*?</p>',
            '<p class="nearby">Outras zonas: '
            + "".join(f'<a href="{p}">{html.escape(n)}</a>' for p, n in ZONES if p != path)
            + "</p>",
            s,
            count=1,
            flags=re.S,
        )
        s = s.replace("</main>", local_section(path) + "</main>", 1)
    has_footer = "<footer" in s
    block = hub(path, with_legal=not has_footer)
    if has_footer:
        s = s.replace("<footer", block + "<footer", 1)
    else:
        s = s.replace("</body>", block + "</body>", 1)
    f.write_text(s, encoding="utf-8")


def write_sitemap():
    urls = [p for p in PAGES if p not in LEGAL]
    body = "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>\n" for p in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + body + "</urlset>\n",
        encoding="utf-8",
    )


def write_llms():
    lines = [
        "# ImpermeabilizaPro",
        "",
        "> Profissional de impermeabilização em Portugal, com base em Sobral de Monte Agraço (distrito de Lisboa). "
        "Responsável: Vinícius Nascimento. Trabalha nos distritos de Lisboa, Santarém, Setúbal e Leiria "
        "(deslocação sujeita à confirmação da localidade). Orçamento sem compromisso por WhatsApp ou telefone.",
        "",
        f"- Telefone e WhatsApp: {PHONE_TXT} (+351)",
        f"- Email: {EMAIL}",
        f"- Google Maps: {MAPS}",
        "- Trabalho completo (materiais e mão de obra) ou só mão de obra, para particulares, condomínios e empreiteiros.",
        "- Não executa trabalhos em telhados de telha/inclinados nem trabalhos em grande altura.",
        "- Não publica preços fixos por m²: o valor depende da área, estado da base, remates, acessos e sistema.",
        "",
        "## Serviços",
        "",
    ]
    lines += [f"- [{full}]({SITE}{p})" for p, _, full in SERVICES]
    lines += ["", "## Zonas", ""]
    lines += [f"- [Impermeabilização em {n}]({SITE}{p})" for p, n in ZONES]
    lines += ["", "## Guias", ""]
    lines += [f"- [{n}]({SITE}{p})" for p, n in GUIDES]
    lines += ["", "## Optional", "", f"- [Informações legais e contactos]({SITE}/informacoes-legais/)", ""]
    (ROOT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    for p in PAGES:
        process(p)
    write_sitemap()
    write_llms()
    print(f"OK: {len(PAGES)} páginas, sitemap ({len(PAGES) - len(LEGAL)} URLs) e llms.txt")
