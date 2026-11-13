#!/usr/bin/env python3
"""Gera as páginas de serviço, preço e localidade, a tabela de preços da página inicial, o sitemap e o llms.txt.

Fonte única do conteúdo: este ficheiro (PAGINAS, LOCAIS). Fonte única dos preços: calculadora/precos.csv.
Uso: python3 scripts/gerar_paginas.py && python3 scripts/harmonizar_layout.py && python3 scripts/verificar_site.py

Regras (AGENTS.md): só fotografias reais, sem avaliações, garantias, certificações ou números inventados;
não anunciar telhados de telha nem trabalhos em grande altura; manter os URLs existentes.
"""
import datetime
import html
import json
import pathlib
import re
import urllib.parse

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://impermeabilizapro.pt"
HOJE = datetime.date.today().isoformat()
NEGOCIO_ID = SITE + "/#negocio"
WA_BASE = "https://wa.me/351930446198?text="
e = lambda s: html.escape(str(s), quote=True)

# ---------------------------------------------------------------- preços (CSV)
_linhas = [l for l in (RAIZ / "calculadora/precos.csv").read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
_cab = _linhas[0].split(";")
CSV = {}
for _l in _linhas[1:]:
    _r = dict(zip(_cab, _l.split(";", len(_cab) - 1)))
    CSV[(_r["grupo"], _r["chave"])] = _r
num = lambda v: float(str(v).replace(",", "."))
cfg = lambda k: num(CSV[("config", k)]["min"])
MIN = int(cfg("minimo_obra_m2"))
IVA = cfg("iva_percentagem")
FATOR = cfg("fator_preco_entrada")


def faixa(g, k):
    r = CSV[(g, k)]
    return num(r["min"]) * FATOR, num(r["max"]) * FATOR


def n0(v):
    return f"{v:,.0f}".replace(",", " ")


def tabela_precos(linhas, titulo="Preços de referência por m²"):
    rows = []
    for g, k in linhas:
        r = CSV[(g, k)]
        a, b = faixa(g, k)
        base = g == "material"
        rot = {"suporte": "Superfície: ", "acesso": "Acesso: ", "remocao": "", "isolamento": "", "acabamento": ""}.get(g, "") + r["descricao"]
        s = "" if base else "+ "
        rows.append(f'<tr><th scope="row">{e(rot)}<small>{"Material e mão de obra" if base else "Acréscimo"}</small></th>'
                    f"<td>{s}{n0(a)}–{n0(b)} €/m²</td><td>{s}{n0(a * (1 + IVA / 100))}–{n0(b * (1 + IVA / 100))} €/m²</td></tr>")
    return (f'<div class="price-table-wrap"><table class="price-table"><caption class="sr-only">{e(titulo)}</caption><thead><tr><th scope="col">Trabalho</th>'
            f'<th scope="col">Sem IVA</th><th scope="col">Com IVA ({IVA:.0f}%)</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def oferta(g, k):
    a, b = faixa(g, k)
    return {"@type": "Offer", "priceCurrency": "EUR", "priceSpecification": {"@type": "UnitPriceSpecification", "minPrice": round(a, 2), "maxPrice": round(b, 2), "priceCurrency": "EUR", "unitText": "m²", "valueAddedTaxIncluded": False}}


# ---------------------------------------------------------------- fotografias reais
F = {
    "gaia_largo": ("g-foto-real-20260915-162859.webp", "Terraço de 440 m² em Vila Nova de Gaia, acabamento mineral"),
    "gaia_rolo": ("g-telhado-real-04.webp", "Primeira camada de tela em cobertura plana"),
    "gaia_obra": ("g-foto-real-20260915-162840.webp", "Terraço em obra nova, Vila Nova de Gaia"),
    "gaia_vista": ("g-foto-real-20260915-161005.webp", "Cobertura plana em obra de construção"),
    "gaia_juntas": ("g-foto-real-20260915-161418.webp", "Sobreposição das faixas de tela"),
    "gaia_remate": ("g-foto-real-20260915-161929.webp", "Remate junto à platibanda"),
    "cobertura_mineral": ("g-obra-real-cobertura-02.webp", "Cobertura plana com acabamento mineral"),
    "cobertura_remates": ("g-telhado-real-01.webp", "Cobertura plana com remates laterais"),
    "cobertura_ralo": ("g-telhado-real-02.webp", "Cobertura com tela aplicada e remates"),
    "terraco_grua": ("g-foto-real-20260917-01.webp", "Terraço em obra nova, antes do acabamento"),
    "terraco_claraboia": ("g-foto-real-20260917-02.webp", "Terraço com remates de claraboia"),
    "terraco_passadico": ("g-foto-real-20260909-151643.webp", "Terraço com tela de armadura e remates"),
    "murete": ("g-obra-terraco-1.webp", "Remate de murete com tela"),
    "parede_maquina": ("g-parede-real-03.webp", "Paredes enterradas em obra de construção"),
    "parede_imperalum": ("g-parede-real-01.webp", "Tela Imperalum em parede enterrada"),
    "parede_fundacao": ("g-parede-real-02.webp", "Tela em parede de cave antes do aterro"),
    "aroeira": ("caso-aroeira-3000m2.webp", "Aroeira: mais de 3.000 m² de paredes enterradas"),
    "ericeira": ("caso-ericeira-200m2.webp", "Ericeira: terraço de cobertura com cerca de 200 m²"),
    "gaia_caso": ("caso-gaia-440m2.webp", "Vila Nova de Gaia: terraço sobre garagem com 440 m²"),
}

# ---------------------------------------------------------------- conteúdo
FAQ_MIN = ("Qual é o mínimo de obra?", f"Trabalhamos em coberturas, terraços e outras áreas planas a partir de {MIN} m². Não fazemos pequenas reparações. Várias zonas da mesma morada somam-se.")
FAQ_IVA = ("Os preços têm IVA?", "Para empresas e construtoras com IVA dedutível, os serviços de construção civil são faturados com autoliquidação (o preço é sem IVA). Para condomínios e particulares aplica-se o IVA à taxa legal: 23%, ou 6% quando a lei o permite.")
FAQ_ZONA = ("Em que zonas trabalham?", "A partir de Sobral de Monte Agraço, nos distritos de Lisboa, Santarém, Setúbal e Leiria. Outras zonas mediante confirmação.")
LINKS_SERV = [("/coberturas-planas/", "Coberturas planas"), ("/terracos/", "Terraços"), ("/paredes/", "Caves e paredes enterradas"), ("/tela-asfaltica/", "Tela asfáltica"),
              ("/impermeabilizacao-condominios/", "Condomínios"), ("/empresas/", "Construtoras"), ("/precos-impermeabilizacao/", "Preços por m²")]
PRECOS_TELA = [("material", "tela_1"), ("material", "tela_2"), ("remocao", "tela_antiga"), ("suporte", "degradado"), ("suporte", "pendentes"), ("acesso", "escadas")]
PRECOS_TERRACO = [("material", "tela_1"), ("material", "tela_2"), ("material", "membrana_liquida"), ("remocao", "tela_antiga"), ("remocao", "sobre_ceramico"), ("suporte", "degradado"), ("suporte", "pendentes"), ("acesso", "escadas")]
PRECOS_TODOS = PRECOS_TERRACO[:3] + [("material", "cimenticia")] + PRECOS_TERRACO[3:] + [("isolamento", "xps"), ("acabamento", "protecao_pesada")]

PAGINAS = {
    "coberturas-planas": dict(
        titulo="Impermeabilização de Coberturas Planas | Preço por m²",
        desc=f"Impermeabilização de coberturas planas de edifícios, armazéns e pavilhões com tela asfáltica ou membrana líquida. A partir de {MIN} m². Veja o preço por m².",
        eyebrow="COBERTURAS PLANAS", h1="Impermeabilização de coberturas planas",
        sub="Edifícios, armazéns, pavilhões e moradias com grandes áreas. Tela asfáltica de uma ou duas camadas, ou membrana líquida.",
        sup="cobertura_plana", fotos=["gaia_largo", "gaia_rolo", "cobertura_mineral", "gaia_juntas", "cobertura_remates", "gaia_remate"],
        inclui=[("Preparação da superfície", "Limpeza, regularização e primário."), ("Tela ou membrana", "Uma ou duas camadas, conforme a exposição."),
                ("Remates e ralos", "Platibandas, muretes, tubos e escoamentos."), ("Acabamento", "Mineral, pintura UV ou proteção pesada.")],
        texto=["Numa cobertura plana, a água entra quase sempre pelos pontos singulares: ralos, encontros com platibandas, juntas e passagens de tubos. Por isso o preço por m² inclui sempre os remates.",
               "Quanto maior a área, mais baixo é o preço por m². Em coberturas acima de 500 m² preparamos proposta com planeamento por fases, para não parar a atividade do edifício."],
        precos=PRECOS_TELA, faq=[("Que sistema usam numa cobertura plana?", "Normalmente tela asfáltica em duas camadas com acabamento mineral quando fica exposta. Em coberturas com muitos remates ou equipamentos, membrana líquida."), FAQ_MIN, FAQ_IVA],
        servico="Impermeabilização de coberturas planas", oferta=("material", "tela_2")),
    "terracos": dict(
        titulo="Impermeabilização de Terraços: Preço por m² | ImpermeabilizaPro",
        desc=f"Impermeabilização de terraços de cobertura, sobre garagens e de condomínios. Tela asfáltica ou membrana líquida, a partir de {MIN} m². Preço por m² na hora.",
        eyebrow="TERRAÇOS", h1="Impermeabilização de terraços",
        sub="Terraços de cobertura, sobre garagens e de condomínios. Com ou sem remoção do sistema antigo.",
        sup="terraco", fotos=["gaia_caso", "ericeira", "terraco_grua", "terraco_claraboia", "terraco_passadico", "murete"],
        inclui=[("Remoção do sistema antigo", "Tela, membrana ou pavimento, quando necessário."), ("Pendentes e regularização", "Para a água não ficar acumulada."),
                ("Impermeabilização", "Tela de uma ou duas camadas, ou membrana líquida."), ("Ralos, soleiras e muretes", "Onde a água entra mais vezes.")],
        texto=["Num terraço transitável, a impermeabilização fica protegida por pavimento ou proteção pesada. Num terraço técnico, a tela pode ficar à vista com acabamento mineral.",
               "Em condomínios preparamos a proposta com preço por m² e total, pronta para levar à assembleia."],
        precos=PRECOS_TERRACO, faq=[("É preciso levantar o pavimento?", "Nem sempre. Em alguns casos aplica-se o sistema sobre o cerâmico existente; noutros, levantar é a única forma de garantir o resultado. Decidimos depois de ver fotografias."), FAQ_MIN, FAQ_IVA],
        servico="Impermeabilização de terraços", oferta=("material", "tela_2")),
    "paredes": dict(
        titulo="Impermeabilização de Caves e Paredes Enterradas | ImpermeabilizaPro",
        desc=f"Impermeabilização de caves, fundações e paredes enterradas com tela asfáltica, em obra nova e reabilitação. A partir de {MIN} m². Preço por m².",
        eyebrow="CAVES E PAREDES ENTERRADAS", h1="Impermeabilização de caves e paredes enterradas",
        sub="Fundações, muros e paredes em contacto com o terreno, em obra nova e reabilitação. Já executámos mais de 3.000 m² numa só obra.",
        sup="cave", fotos=["aroeira", "parede_maquina", "parede_imperalum", "parede_fundacao"],
        inclui=[("Preparação da parede", "Limpeza, regularização e primário."), ("Tela asfáltica", "Tela com armadura em poliéster, soldada a maçarico."),
                ("Remates na fundação", "Encontro com a sapata e juntas."), ("Coordenação com a obra", "Antes do aterro, no planeamento da construtora.")],
        texto=["Em obra nova, a impermeabilização de paredes enterradas tem de ser feita antes do aterro: depois, o acesso é muito mais caro. Trabalhamos no planeamento da construtora.",
               "Na obra da Aroeira, com mais de 3.000 m² de paredes enterradas, aplicámos tela Imperalum com armadura em poliéster."],
        precos=[("material", "tela_1"), ("material", "tela_2"), ("material", "cimenticia"), ("suporte", "degradado")],
        faq=[("Fazem só a mão de obra?", "Sim. Trabalhamos com material e mão de obra ou só a execução, em subempreitada."), FAQ_MIN, FAQ_IVA],
        servico="Impermeabilização de caves e paredes enterradas", oferta=("material", "tela_1")),
    "tela-asfaltica": dict(
        titulo="Aplicação de Tela Asfáltica em Coberturas e Terraços | ImpermeabilizaPro",
        desc=f"Aplicação de tela asfáltica de uma ou duas camadas em coberturas, terraços e paredes enterradas. A partir de {MIN} m². Veja o preço por m².",
        eyebrow="TELA ASFÁLTICA", h1="Aplicação de tela asfáltica",
        sub="Uma ou duas camadas, soldadas a maçarico, com ou sem acabamento mineral. Coberturas, terraços e paredes enterradas.",
        sup="cobertura_plana", fotos=["gaia_rolo", "gaia_obra", "gaia_juntas", "parede_imperalum"],
        inclui=[("Primário", "Para a tela aderir ao suporte."), ("Uma ou duas camadas", "Duas camadas em coberturas expostas."),
                ("Sobreposições e remates", "Juntas soldadas, ralos e platibandas."), ("Acabamento mineral", "Quando a tela fica à vista.")],
        texto=["A tela asfáltica é a solução mais usada em coberturas planas e terraços em Portugal. Em coberturas expostas recomendamos duas camadas, com a segunda autoprotegida com acabamento mineral.",
               "Usámos tela Imperalum nas obras que mostramos."],
        precos=PRECOS_TELA, faq=[("Uma ou duas camadas?", "Duas camadas em coberturas e terraços expostos; uma camada pode bastar em paredes enterradas ou sob proteção pesada."), FAQ_MIN, FAQ_IVA],
        servico="Aplicação de tela asfáltica", oferta=("material", "tela_2")),
    "impermeabilizacao-terraco-preco": dict(
        titulo="Preço de Impermeabilização de Terraço por m² (2026)",
        desc=f"Quanto custa impermeabilizar um terraço em 2026: preços por m² com e sem IVA, acréscimos e calculadora. Obras a partir de {MIN} m².",
        eyebrow="PREÇO · TERRAÇOS", h1="Quanto custa impermeabilizar um terraço?",
        sub="Preços por m² com e sem IVA, e o que faz o preço subir. Calcule o valor para a sua obra.",
        sup="terraco", fotos=["gaia_caso", "terraco_claraboia", "ericeira"], precos_topo=True,
        inclui=[("Material e mão de obra", "Os preços da tabela incluem os dois."), ("O que faz subir", "Remoção, regularização, pendentes e acessos."),
                ("O que faz descer", "Áreas grandes e superfícies em bom estado."), ("IVA", "Autoliquidação para empresas; 23% para condomínios e particulares.")],
        texto=[f"Os valores são indicativos, para obras a partir de {MIN} m² com acesso fácil. O valor final é confirmado depois de vermos fotografias ou a obra."],
        precos=PRECOS_TERRACO, faq=[("Porque é que o preço por m² desce em áreas grandes?", "Os custos de montagem, deslocação e remates pesam menos quando a área é maior."), FAQ_IVA, FAQ_MIN],
        servico="Impermeabilização de terraços", oferta=("material", "tela_2")),
    "tela-asfaltica-preco": dict(
        titulo="Preço da Tela Asfáltica Aplicada por m² (2026)",
        desc=f"Preço da tela asfáltica aplicada por m² em 2026, com e sem IVA: uma camada, duas camadas e acréscimos. Obras a partir de {MIN} m².",
        eyebrow="PREÇO · TELA ASFÁLTICA", h1="Quanto custa aplicar tela asfáltica?",
        sub="Preço por m² da tela aplicada, com material e mão de obra. Com e sem IVA.",
        sup="cobertura_plana", fotos=["gaia_rolo", "gaia_juntas", "gaia_largo"], precos_topo=True,
        inclui=[("Uma camada", "Paredes enterradas e superfícies protegidas."), ("Duas camadas", "Coberturas e terraços expostos."),
                ("Remoção da tela antiga", "Quando a antiga já não adere."), ("Acessos", "Prédios sem elevador custam mais.")],
        texto=[f"Os valores são indicativos, para obras a partir de {MIN} m². O valor final é confirmado depois de vermos a obra."],
        precos=PRECOS_TELA, faq=[("A tela antiga tem de ser retirada?", "Se estiver descolada, com bolhas ou várias camadas sobrepostas, sim. Se estiver aderente, pode servir de base."), FAQ_IVA, FAQ_MIN],
        servico="Aplicação de tela asfáltica", oferta=("material", "tela_2")),
    "reparacao-infiltracoes": dict(
        titulo="Infiltrações em Coberturas e Terraços | ImpermeabilizaPro",
        desc=f"Infiltrações em coberturas planas e terraços de prédios, armazéns e condomínios: renovação completa da impermeabilização a partir de {MIN} m².",
        eyebrow="INFILTRAÇÕES", h1="Infiltrações em coberturas e terraços",
        sub=f"Quando a impermeabilização já não protege, renovamos o sistema inteiro. Não fazemos pequenas reparações pontuais: trabalhamos a partir de {MIN} m².",
        sup="cobertura_plana", fotos=["terraco_passadico", "gaia_remate", "cobertura_ralo"],
        inclui=[("Diagnóstico por fotografias", "Ralos, juntas, remates e estado da tela."), ("Remoção do sistema antigo", "Quando já não adere ou tem várias camadas."),
                ("Nova impermeabilização", "Tela ou membrana em toda a área."), ("Remates", "Onde a água entra mais vezes.")],
        texto=["Uma mancha no teto raramente está por baixo do ponto onde a água entra. Por isso, em coberturas com vários anos, remendar costuma adiar o problema: renovar a impermeabilização em toda a área resolve-o."],
        precos=PRECOS_TELA[:4], faq=[("Fazem reparações pequenas?", f"Não. Fazemos a renovação da impermeabilização em coberturas e áreas planas a partir de {MIN} m²."), FAQ_IVA, FAQ_ZONA],
        servico="Renovação de impermeabilização com infiltrações", oferta=("material", "tela_2")),
    "humidade-parede-exterior": dict(
        titulo="Humidade em Paredes Exteriores e Enterradas | ImpermeabilizaPro",
        desc=f"Impermeabilização de paredes exteriores até ao 1.º piso e paredes enterradas com humidade. Obras a partir de {MIN} m². Preço por m².",
        eyebrow="PAREDES", h1="Humidade em paredes exteriores e enterradas",
        sub="Paredes encostadas ao terreno, muros e paredes exteriores até ao 1.º piso. Não fazemos trabalhos em grande altura.",
        sup="cave", fotos=["parede_imperalum", "parede_fundacao", "parede_maquina"],
        inclui=[("Origem da humidade", "Terreno, chuva batida ou capilaridade."), ("Paredes enterradas", "Tela asfáltica antes do aterro."),
                ("Paredes exteriores", "Membrana cimentícia ou líquida."), ("Sem grande altura", "Até ao 1.º piso.")],
        texto=["Numa parede enterrada, a água vem do terreno e a solução é pelo lado de fora, antes do aterro. Numa parede exterior, a chuva batida entra por fissuras e juntas: aí usamos membranas cimentícias ou líquidas."],
        precos=[("material", "cimenticia"), ("material", "membrana_liquida"), ("material", "tela_1"), ("suporte", "degradado")],
        faq=[("Fazem fachadas de prédios?", "Só até ao 1.º piso, sem andaimes de grande altura."), FAQ_MIN, FAQ_IVA],
        servico="Impermeabilização de paredes", oferta=("material", "cimenticia")),
    "casas-de-banho": dict(
        titulo="Impermeabilização de Casas de Banho | ImpermeabilizaPro",
        desc="Impermeabilização de casas de banho e zonas húmidas interiores antes do revestimento. Serviço à parte, orçamentado depois de vermos fotografias.",
        eyebrow="CASAS DE BANHO", h1="Impermeabilização de casas de banho",
        sub="Zonas de duche, cantos e passagens de tubos, antes do revestimento. É um serviço à parte: orçamentamos depois de ver fotografias.",
        sup=None, fotos=[],
        inclui=[("Antes do revestimento", "Em remodelações e obra nova."), ("Membrana líquida ou cimentícia", "Compatível com a cola e o azulejo."),
                ("Cantos e tubagens", "Com bandas de reforço."), ("Para empreiteiros", "Integrado no planeamento da remodelação.")],
        texto=["O mínimo de 100 m² aplica-se a coberturas e áreas planas, não a casas de banho. Envie fotografias, a fase da obra e a localidade."],
        precos=[], faq=[("Conseguem dar preço por m²?", "Nas casas de banho o preço depende sobretudo dos cantos, tubagens e bases de duche, por isso orçamentamos depois de ver fotografias."), FAQ_IVA, FAQ_ZONA],
        servico="Impermeabilização de casas de banho", oferta=None,
        wa="Olá, preciso de impermeabilizar uma casa de banho. A obra fica em [localidade]. Posso enviar fotografias."),
    "empresas": dict(
        titulo="Subempreitada de Impermeabilização para Construtoras | ImpermeabilizaPro",
        desc=f"Subempreitada de impermeabilização para construtoras e empreiteiros: coberturas, terraços e paredes enterradas. Com material ou só mão de obra. A partir de {MIN} m².",
        eyebrow="CONSTRUTORAS E EMPREITEIROS", h1="Subempreitada de impermeabilização para construtoras",
        sub="Coberturas, terraços e paredes enterradas, com material e mão de obra ou só a execução. Integrados no planeamento da sua obra.",
        sup="terraco", cliente="empresa", fotos=["aroeira", "parede_maquina", "gaia_obra", "terraco_grua"],
        inclui=[("Proposta por m²", "A partir das medições ou do caderno de encargos."), ("Com material ou só execução", "Como for melhor para a obra."),
                ("Faturação", "Autoliquidação do IVA em serviços de construção civil."), ("Obras grandes", "Já executámos mais de 3.000 m² numa só obra.")],
        texto=["Envie as medições, a planta ou o mapa de quantidades e a data prevista. Respondemos com preço por m², o que está incluído e a disponibilidade.",
               "Estamos a começar parcerias com construtoras na região de Lisboa e Oeste, com preços de entrada abaixo do mercado."],
        precos=PRECOS_TELA[:2] + [("material", "membrana_liquida")], faq=[("Como é faturado o IVA?", "Nos serviços de construção civil para empresas com IVA dedutível aplica-se a autoliquidação: a fatura sai sem IVA e é o adquirente que o liquida."), ("Fazem só a mão de obra?", "Sim, quando a construtora fornece o material."), FAQ_MIN],
        servico="Subempreitada de impermeabilização", oferta=("material", "tela_2"),
        wa="Olá, sou de uma construtora e queria uma proposta de impermeabilização. A obra tem cerca de [m²] e fica em [localidade]. Posso enviar medições."),
    "impermeabilizacao-condominios": dict(
        titulo="Impermeabilização de Terraços de Condomínios | Preço por m²",
        desc=f"Impermeabilização de terraços de cobertura e coberturas planas de condomínios. Proposta clara com preço por m² e total para a assembleia. A partir de {MIN} m².",
        eyebrow="CONDOMÍNIOS E ADMINISTRAÇÕES", h1="Impermeabilização de terraços de condomínios",
        sub="Terraços de cobertura e coberturas planas de prédios. Proposta com preço por m² e total, pronta para a assembleia.",
        sup="terraco", cliente="condominio", fotos=["gaia_caso", "cobertura_mineral", "terraco_passadico"],
        inclui=[("Proposta para a assembleia", "Preço por m², total com IVA e o que inclui."), ("Acessos", "Prédios com ou sem elevador."),
                ("Pouco incómodo", "Trabalho no terraço, sem entrar nas frações."), ("Remates e ralos", "Onde as infiltrações começam.")],
        texto=["Em prédios, a infiltração do último andar vem muitas vezes do terraço de cobertura. Uma renovação completa custa menos do que reparações repetidas.",
               "Envie fotografias do terraço e a área aproximada; a administração recebe a proposta por escrito."],
        precos=PRECOS_TERRACO, faq=[("O IVA é de 23%?", "Para condomínios aplica-se a taxa legal: 23%, ou 6% em obras de reparação de habitação quando os materiais não passam de 20% do valor."), FAQ_MIN, FAQ_ZONA],
        servico="Impermeabilização de terraços de condomínios", oferta=("material", "tela_2"),
        wa="Olá, sou da administração de um condomínio e queria uma proposta para impermeabilizar o terraço. Tem cerca de [m²] e fica em [localidade]."),
    "precos-impermeabilizacao": dict(
        titulo="Preços de Impermeabilização por m² em 2026 | ImpermeabilizaPro",
        desc=f"Tabela de preços de impermeabilização por m² em 2026: tela asfáltica, membrana líquida e cimentícia, com e sem IVA, e acréscimos. Obras a partir de {MIN} m².",
        eyebrow="PREÇOS 2026", h1="Preços de impermeabilização por m²",
        sub="Tabela de preços com e sem IVA, para obras a partir de 100 m². Para o valor da sua obra, use a calculadora.",
        sup=None, fotos=["gaia_largo", "aroeira", "ericeira"], precos_topo=True,
        inclui=[("Preço base", "Material e mão de obra por m²."), ("Acréscimos", "Somam-se quando se aplicam."),
                ("Escala", "Acima de 200 m² o preço por m² desce."), ("IVA", "Autoliquidação para empresas; taxa legal para os restantes.")],
        texto=[f"Os preços são indicativos para obras a partir de {MIN} m², com acesso fácil, na zona de Lisboa e Oeste. Estamos a criar parcerias e praticamos preços de entrada abaixo das referências de mercado."],
        precos=PRECOS_TODOS, faq=[FAQ_IVA, FAQ_MIN, ("O preço inclui deslocação?", "Na zona de Sobral de Monte Agraço e Oeste, sim. Para Lisboa, Santarém, Setúbal e Leiria pode haver um pequeno acréscimo, que a calculadora já inclui.")],
        servico="Impermeabilização", oferta=("material", "tela_1")),
}

LOCAIS = {
    "sobral-de-monte-agraco": dict(nome="Sobral de Monte Agraço", nova=True,
        freg=["Sobral de Monte Agraço", "Santo Quintino", "Sapataria"],
        fatores=[("A nossa base", "Trabalhamos a partir de Sobral de Monte Agraço: sem custos extra de deslocação no concelho."), ("Moradias e armazéns", "Coberturas planas de armazéns, pavilhões agrícolas e moradias com terraços grandes.")]),
    "alenquer": dict(nome="Alenquer", nova=True,
        freg=["Abrigada e Cabanas de Torres", "Aldeia Galega da Merceana e Aldeia Gavinha", "Alenquer (Santo Estêvão e Triana)", "Carnota", "Carregado e Cadafais", "Meca", "Olhalvo", "Ota", "Ribafria e Pereiro de Palhacana", "Ventosa", "Vila Verde dos Francos"],
        fatores=[("Armazéns e logística", "No Carregado e junto à A1 há muitos armazéns com coberturas planas de grande área."), ("Moradias no interior", "Terraços e anexos em moradias, onde a área total passa facilmente dos 100 m².")]),
    "arruda-dos-vinhos": dict(nome="Arruda dos Vinhos", nova=True,
        freg=["Arranhó", "Arruda dos Vinhos", "Cardosas", "Santiago dos Velhos"],
        fatores=[("Perto da nossa base", "Concelho vizinho de Sobral de Monte Agraço: sem custos extra de deslocação."), ("Moradias e adegas", "Terraços de moradias e coberturas de armazéns agrícolas.")]),
    "vila-franca-de-xira": dict(nome="Vila Franca de Xira", nova=True,
        freg=["Alhandra, São João dos Montes e Calhandriz", "Alverca do Ribatejo e Sobralinho", "Castanheira do Ribatejo e Cachoeiras", "Póvoa de Santa Iria e Forte da Casa", "Vialonga", "Vila Franca de Xira"],
        fatores=[("Indústria e logística", "Armazéns e pavilhões com coberturas planas em Alverca, Castanheira e Vialonga."), ("Prédios e condomínios", "Terraços de cobertura em Póvoa de Santa Iria, Forte da Casa e Vila Franca.")]),
    "mafra": dict(nome="Mafra",
        freg=["Azueira e Sobral da Abelheira", "Carvoeira", "Encarnação", "Enxara do Bispo, Gradil e Vila Franca do Rosário", "Ericeira", "Igreja Nova e Cheleiros", "Mafra", "Malveira e São Miguel de Alcainça", "Milharado", "Santo Isidoro", "Venda do Pinheiro e Santo Estêvão das Galés"],
        fatores=[("Perto do mar", "Na Ericeira e na costa, o vento e a maresia desgastam mais depressa as telas expostas: o acabamento mineral protege-as."), ("Obra feita no concelho", "Terraço de cobertura com cerca de 200 m² na Ericeira.")], fotos=["ericeira", "gaia_largo", "murete"]),
    "torres-vedras": dict(nome="Torres Vedras",
        freg=["A dos Cunhados e Maceira", "Campelos e Outeiro da Cabeça", "Carvoeira e Carmões", "Dois Portos e Runa", "Freiria", "Maxial e Monte Redondo", "Ponte do Rol", "Ramalhal", "Santa Maria, São Pedro e Matacães", "São Pedro da Cadeira", "Silveira", "Turcifal", "Ventosa"],
        fatores=[("Chuva com vento", "No Oeste a chuva vem batida pelo vento e entra sobretudo por remates, platibandas e soleiras."), ("Armazéns e moradias", "Coberturas planas de armazéns e terraços de moradias com grandes áreas.")]),
    "loures": dict(nome="Loures",
        freg=["Bucelas", "Camarate, Unhos e Apelação", "Fanhões", "Loures", "Lousa", "Moscavide e Portela", "Sacavém e Prior Velho", "Santa Iria de Azoia, São João da Talha e Bobadela", "Santo Antão e São Julião do Tojal", "Santo António dos Cavaleiros e Frielas"],
        fatores=[("Prédios e condomínios", "Muitos terraços de cobertura em Sacavém, Moscavide, Portela e Santo António dos Cavaleiros."), ("Indústria", "Armazéns em São João da Talha, Bobadela e Prior Velho com coberturas planas grandes.")]),
    "sintra": dict(nome="Sintra",
        freg=["Agualva e Mira-Sintra", "Algueirão-Mem Martins", "Almargem do Bispo, Pêro Pinheiro e Montelavar", "Cacém e São Marcos", "Casal de Cambra", "Colares", "Massamá e Monte Abraão", "Queluz e Belas", "Rio de Mouro", "São João das Lampas e Terrugem", "Sintra (Santa Maria e São Miguel, São Martinho e São Pedro de Penaferrim)"],
        fatores=[("Humidade e nevoeiro", "Perto da serra as superfícies demoram a secar: marcamos a aplicação para dias secos."), ("Condomínios e caves", "Terraços de prédios em Queluz, Cacém e Algueirão; caves em terrenos inclinados.")]),
    "lisboa": dict(nome="Lisboa", freg=[],
        fatores=[("Edifícios antigos", "Terraços de cobertura com várias camadas antigas: muitas vezes é preciso remover antes de impermeabilizar."), ("Logística na cidade", "Acesso, estacionamento e licença de ocupação da via pública quando há contentor ou andaime.")]),
}
FOTOS_LOCAL = [["gaia_largo", "cobertura_mineral", "terraco_claraboia"], ["gaia_caso", "parede_imperalum", "gaia_rolo"], ["terraco_grua", "gaia_juntas", "aroeira"]]
for i, (slug, d) in enumerate(LOCAIS.items()):
    n = d["nome"]
    PAGINAS["impermeabilizacao-" + slug] = dict(
        titulo=f"Impermeabilização em {n}: Coberturas e Terraços | ImpermeabilizaPro",
        desc=f"Impermeabilização de coberturas planas, terraços e caves em {n}, para construtoras, condomínios e empresas. A partir de {MIN} m². Veja o preço por m².",
        eyebrow=f"IMPERMEABILIZAÇÃO · {n.upper()}", h1=f"Impermeabilização em {n}",
        sub=f"Coberturas planas, terraços e caves em {n}, para construtoras, condomínios e empresas. Obras a partir de {MIN} m².",
        sup=None, fotos=d.get("fotos", FOTOS_LOCAL[i % 3]), local=d,
        inclui=[(t, x) for t, x in d["fatores"]] + [("Preço por m² na hora", "Use a calculadora ou envie fotografias pelo WhatsApp.")],
        texto=[], precos=PRECOS_TELA[:3],
        faq=[(f"Fazem obras de impermeabilização em {n}?", f"Sim. Trabalhamos a partir de Sobral de Monte Agraço e fazemos obras em {n}."), FAQ_MIN, FAQ_IVA],
        servico=f"Impermeabilização em {n}", oferta=("material", "tela_2"), area=n)


# ---------------------------------------------------------------- HTML
def figura(k):
    img, cap = F[k]
    w, h = (1200, 675) if img.startswith("caso-") else (600, 450)
    return f'<figure><img src="/assets/{img}" alt="{e(cap)}" width="{w}" height="{h}" loading="lazy"><figcaption>{e(cap)}</figcaption></figure>'


def minimo_span(t):
    return e(t).replace(f"{MIN} m²", f'<span data-minimo-obra>{MIN}</span> m²')


def pagina(slug, p):
    url = f"{SITE}/{slug}/"
    wa = WA_BASE + urllib.parse.quote(p.get("wa", "Olá, gostaria de pedir uma proposta de impermeabilização. A obra tem cerca de [m²] e fica em [localidade]."))
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    serv = {"@context": "https://schema.org", "@type": "Service", "name": p["servico"], "serviceType": "Impermeabilização", "url": url,
            "provider": {"@type": "HomeAndConstructionBusiness", "@id": NEGOCIO_ID, "name": "ImpermeabilizaPro", "telephone": "+351930446198", "url": SITE + "/"},
            "areaServed": [{"@type": "AdministrativeArea", "name": p.get("area")}] if p.get("area") else [{"@type": "AdministrativeArea", "name": n} for n in ("Distrito de Lisboa", "Distrito de Santarém", "Distrito de Setúbal", "Distrito de Leiria")]}
    if p.get("oferta"):
        serv["offers"] = oferta(*p["oferta"])
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Início", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": p["h1"], "item": url}]}
    calc = ""
    if p.get("sup") is not False and slug != "casas-de-banho":
        attrs = (f' data-superficie="{p["sup"]}"' if p.get("sup") else "") + (f' data-cliente="{p["cliente"]}"' if p.get("cliente") else "")
        calc = (f'<div class="calc" data-calc data-modo="rapido"{attrs}><h2>Preço por m² em 30 segundos</h2><form data-calc-form novalidate><p class="calc-vazio">A carregar a calculadora…</p></form>'
                f'<div class="calc-res" data-calc-result aria-live="polite"></div><div class="calc-acoes" id="calcAcoes" hidden><a class="btn whatsapp big" id="calcWa" data-placement="calculadora_{slug}" href="https://wa.me/351930446198" target="_blank" rel="noopener noreferrer">Pedir proposta pelo WhatsApp</a>'
                f'<a class="btn outline big" href="tel:+351930446198" data-track="phone_calculadora">Ligar</a></div><p class="calc-legal">Estimativa indicativa, não é orçamento. O WhatsApp abre com os dados preenchidos; só nos chega quando carregar em Enviar.</p>'
                f'<noscript><p class="calc-aviso">A calculadora precisa de JavaScript. Ligue 930 446 198 ou use o WhatsApp.</p></noscript></div>')
    else:
        calc = (f'<div class="calc"><h2>Peça o orçamento</h2><p>Envie fotografias, a fase da obra e a localidade.</p><div class="calc-acoes"><a class="btn whatsapp big wa-direct" data-placement="hero_{slug}" href="{wa}" target="_blank" rel="noopener noreferrer">Enviar fotografias pelo WhatsApp</a>'
                f'<a class="btn outline big" href="tel:+351930446198" data-track="phone_hero">Ligar</a></div></div>')
    fotos = "".join(figura(k) for k in p["fotos"])
    sec_fotos = f'<section class="h-sec" id="obras"><div class="wrap"><h2>Obras reais</h2><div class="h-galeria h-galeria-{min(len(p["fotos"]), 6)}">{fotos}</div></div></section>' if fotos else ""
    inclui = "".join(f"<li><strong>{e(t)}</strong><span>{minimo_span(x)}</span></li>" for t, x in p["inclui"])
    texto = "".join(f"<p>{minimo_span(t)}</p>" for t in p["texto"])
    local = ""
    if p.get("local"):
        d = p["local"]
        fr = f'<p><strong>Freguesias do concelho:</strong> {e("; ".join(d["freg"]))}.</p>' if d["freg"] else "<p><strong>Toda a cidade de Lisboa</strong>, sujeito às condições de acesso da obra.</p>"
        local = fr
    precos = ""
    if p["precos"]:
        precos = (f'<section class="h-sec soft" id="precos"><div class="wrap"><h2>Preços de referência por m²</h2><p class="h-lead">Material e mão de obra, para obras a partir de <span data-minimo-obra>{MIN}</span> m² com acesso fácil. Preços de entrada, abaixo das referências de mercado.</p>'
                  f'{tabela_precos(p["precos"])}<p class="calc-legal">Valores indicativos, não são orçamento. A calculadora junta os acréscimos e o desconto por área. Atualizado em {HOJE}.</p></div></section>')
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{minimo_span(a)}</p></details>" for q, a in p["faq"])
    links = "".join(f'<a href="{u}">{e(t)}</a>' for u, t in LINKS_SERV if u != f"/{slug}/")
    zonas = "".join(f'<a href="/impermeabilizacao-{s}/">{e(d["nome"])}</a>' for s, d in LOCAIS.items() if f"impermeabilizacao-{s}" != slug)
    ordem_precos_topo = p.get("precos_topo")
    corpo = (f'<section class="h-hero slim" id="pedido"><img src="/assets/foto-real-20260915-162914-1600.webp" srcset="/assets/foto-real-20260915-162914-800.webp 800w, /assets/foto-real-20260915-162914-1600.webp 1600w" sizes="100vw" alt="" width="1920" height="1080" fetchpriority="high">'
             f'<div class="wrap h-hero-in"><div><p class="h-crumbs"><a href="/">Início</a> › {e(p["h1"])}</p><p class="h-eyebrow">{e(p["eyebrow"])}</p><h1>{e(p["h1"])}</h1><p class="h-sub">{minimo_span(p["sub"])}</p>'
             f'<ul class="h-chips"><li>Obras a partir de <span data-minimo-obra>{MIN}</span> m²</li><li>Preços de entrada</li><li>Fotografias reais</li></ul>'
             f'<p>Prefere falar? <a class="h-tel" href="tel:+351930446198" data-track="phone_hero">930 446 198</a> · Vinícius Nascimento</p></div>{calc}</div></section>\n')
    corpo += (precos if ordem_precos_topo else sec_fotos)
    corpo += f'<section class="h-sec{" soft" if not ordem_precos_topo else ""}"><div class="wrap"><h2>{"O que inclui" if not p.get("local") else "Em " + e(p["local"]["nome"])}</h2><ul class="h-inclui">{inclui}</ul>'
    corpo += f'<div class="h-texto" style="margin-top:18px">{texto}{local}</div></div></section>\n'
    corpo += (sec_fotos if ordem_precos_topo else precos)
    corpo += f'<section class="h-sec h-faq" id="faq"><div class="wrap narrow"><h2>Perguntas frequentes</h2>{faq}</div></section>\n'
    corpo += (f'<section class="h-sec soft"><div class="wrap"><div class="h-cta"><div><h2>Tem uma obra a partir de <span data-minimo-obra>{MIN}</span> m²?</h2><p>Envie medidas e fotografias. Respondemos com preço por m² e total.</p></div>'
              f'<a class="btn whatsapp big wa-direct" data-placement="cta_final" href="{wa}" target="_blank" rel="noopener noreferrer">Pedir proposta pelo WhatsApp</a></div>'
              f'<h2 style="margin-top:28px;font-size:1.2rem">Outros serviços</h2><div class="h-links">{links}</div><h2 style="margin-top:20px;font-size:1.2rem">Zonas</h2><div class="h-links">{zonas}</div></div></section>')
    modulo = '<script type="module" src="/calculadora/widget.mjs?v=20261113-5"></script>' if 'data-calc ' in calc or 'data-calc>' in calc else ""
    return f'''<!doctype html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{e(p["titulo"])}</title>
<meta name="description" content="{e(p["desc"])}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:locale" content="pt_PT"><meta property="og:url" content="{url}">
<meta property="og:title" content="{e(p["titulo"])}"><meta property="og:description" content="{e(p["desc"])}">
<meta property="og:image" content="{SITE}/assets/foto-real-20260915-162914.jpeg"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0a2340">
<link rel="icon" href="/assets/logo-impermeabilizapro.webp" type="image/webp">
<link rel="preload" as="image" href="/assets/foto-real-20260915-162914-800.webp" imagesrcset="/assets/foto-real-20260915-162914-800.webp 800w, /assets/foto-real-20260915-162914-1600.webp 1600w" imagesizes="100vw">
<link rel="stylesheet" href="/style.css?v=20260919-local4">
<link rel="stylesheet" href="/calculadora/calc.css?v=20261113-5">
<link rel="stylesheet" href="/assets/b2b.css?v=20261113-2">
<script type="application/ld+json">{json.dumps(serv, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(crumbs, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
</head>
<body class="pagina-b2b">
<header class="header"></header>
<main id="conteudo">
{corpo}
</main>
<footer></footer>
{modulo}
</body>
</html>
'''


def tabela_home():
    p = RAIZ / "index.html"
    s = p.read_text(encoding="utf-8")
    bloco = (f'<!-- precos-referencia:inicio -->\n<section class="h-sec soft" id="precos"><div class="wrap"><h2>Preços de referência por m²</h2>'
             f'<p class="h-lead">Material e mão de obra, para obras a partir de <span data-minimo-obra>{MIN}</span> m² com acesso fácil. Preços de entrada, abaixo das referências de mercado.</p>'
             f'{tabela_precos(PRECOS_TERRACO[:3] + [("remocao", "tela_antiga"), ("suporte", "degradado"), ("acesso", "escadas")])}'
             f'<p style="margin-top:14px"><a class="btn whatsapp big" href="/precos-impermeabilizacao/">Ver todos os preços</a></p></div></section>\n<!-- precos-referencia:fim -->')
    s = re.sub(r"<!-- precos-referencia:inicio -->.*?<!-- precos-referencia:fim -->", bloco, s, flags=re.S)
    p.write_text(s, encoding="utf-8")


def sitemap():
    urls = ["", "calculadora/"] + [f"{s}/" for s in PAGINAS]
    corpo = "".join(f"  <url><loc>{SITE}/{u}</loc><lastmod>{HOJE}</lastmod></url>\n" for u in urls)
    (RAIZ / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{corpo}</urlset>\n', encoding="utf-8")


def llms():
    linhas = [f"- {CSV[(g, k)]['descricao']}: {n0(faixa(g, k)[0])}–{n0(faixa(g, k)[1])} €/m² sem IVA" + (" (material e mão de obra)" if g == "material" else " (acréscimo)") for g, k in PRECOS_TODOS]
    txt = f"""# ImpermeabilizaPro

> Impermeabilização de coberturas planas, terraços, caves e paredes enterradas para construtoras, condomínios e empresas, em Portugal (distritos de Lisboa, Santarém, Setúbal e Leiria). Base em Sobral de Monte Agraço. Responsável: Vinícius Nascimento (5 anos de experiência). Obras a partir de {MIN} m².

## Factos
- Serviços: coberturas planas, terraços, caves e paredes enterradas, aplicação de tela asfáltica (uma ou duas camadas), membranas líquidas e cimentícias, subempreitada para construtoras. Casas de banho: serviço à parte.
- Não faz: pequenas reparações, telhados de telha ou inclinados, trabalhos em grande altura.
- Mínimo de obra: {MIN} m² em coberturas e áreas planas.
- Obras reais: Aroeira (mais de 3.000 m² de paredes enterradas, tela Imperalum), Vila Nova de Gaia (terraço sobre garagem, 440 m², duas camadas), Ericeira (terraço de cobertura, cerca de 200 m²).
- IVA: autoliquidação para empresas com IVA dedutível (serviços de construção civil); 23% para condomínios e particulares (6% quando a lei o permite).
- Contacto: +351 930 446 198 (telefone e WhatsApp), proimpermeabiliza@gmail.com.

## Preços indicativos (atualizado em {HOJE}, obras a partir de {MIN} m², acesso fácil)
""" + "\n".join(linhas) + f"""
- Áreas maiores têm preço por m² mais baixo (a partir de 200 m², 500 m² e 1000 m²).

## Páginas
- [Calculadora de preço por m²]({SITE}/calculadora/)
- [Preços de impermeabilização por m²]({SITE}/precos-impermeabilizacao/)
""" + "\n".join(f"- [{p['h1']}]({SITE}/{s}/)" for s, p in PAGINAS.items() if s != "precos-impermeabilizacao") + "\n"
    (RAIZ / "llms.txt").write_text(txt, encoding="utf-8")


if __name__ == "__main__":
    for slug, p in PAGINAS.items():
        d = RAIZ / slug
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(pagina(slug, p), encoding="utf-8")
    tabela_home()
    sitemap()
    llms()
    print(f"{len(PAGINAS)} páginas geradas, sitemap e llms.txt atualizados.")
