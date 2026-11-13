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
AUTOLIQ = cfg("autoliquidacao_ativa") == 1
IVA_CURTO = "Autoliquidação para empresas; taxa legal para os restantes." if AUTOLIQ else "IVA à taxa legal (23%); dedutível para empresas."
IVA_LONGO = ("Para empresas e construtoras com IVA dedutível, os serviços de construção civil são faturados com autoliquidação (o preço é sem IVA). Para condomínios e particulares aplica-se o IVA à taxa legal: 23%, ou 6% quando a lei o permite." if AUTOLIQ else "Aplicamos o IVA à taxa legal: 23%, ou 6% nas obras de habitação em que a lei o permite. Para empresas com IVA dedutível, o valor que conta é o preço sem IVA, que mostramos sempre.")


MARGEM = cfg("margem_base_percentagem") / 100


def linha(g, k):
    """Linha do CSV; ("mo", material) = só mão de obra desse material (material × fator «cliente fornece»)."""
    if g == "mo":
        r = dict(CSV[("material", k)])
        f = num(CSV[("fornecimento", "cliente")]["min"])
        r.update(min=str(num(r["min"]) * f), max=str(num(r["max"]) * f), descricao="Só mão de obra: " + r["descricao"].lower().replace(" (sistema multicamada)", "") + " (material do cliente)",
                 origem=r["origem"] + " · " + CSV[("fornecimento", "cliente")]["origem"])
        return r
    return CSV[(g, k)]


def faixa(g, k):
    """Preço publicado: valor médio da linha × fator de entrada, ± a margem da calculadora (igual à calculadora)."""
    r = linha(g, k)
    medio = (num(r["min"]) + num(r["max"])) / 2 * FATOR
    return medio * (1 - MARGEM), medio * (1 + MARGEM)


def n0(v):
    return f"{v:,.0f}".replace(",", " ")


def com_fonte(linhas):
    """Só publica valores com fonte: as linhas marcadas HIPÓTESE ficam só na calculadora."""
    return [(g, k) for g, k in linhas if "HIPÓTESE" not in linha(g, k)["origem"]]


def tabela_precos(linhas, titulo="Preços de referência por m²"):
    rows = []
    for g, k in com_fonte(linhas):
        r = linha(g, k)
        a, b = faixa(g, k)
        base = g in ("material", "mo")
        rot = {"suporte": "Superfície: ", "acesso": "Acesso: ", "remocao": "", "isolamento": "", "acabamento": ""}.get(g, "") + r["descricao"]
        s = "" if base else "+ "
        rows.append(f'<tr><th scope="row">{e(rot)}<small>{("Só mão de obra" if g == "mo" else "Material e mão de obra") if base else "Acréscimo"}</small></th>'
                    f"<td>{s}{n0(a)}–{n0(b)} €/m²</td><td>{s}{n0(a * (1 + IVA / 100))}–{n0(b * (1 + IVA / 100))} €/m²</td></tr>")
    return (f'<div class="price-table-wrap"><table class="price-table"><caption class="sr-only">{e(titulo)}</caption><thead><tr><th scope="col">Trabalho</th>'
            f'<th scope="col">Sem IVA</th><th scope="col">Com IVA ({IVA:.0f}%)</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def oferta(g, k):
    a, b = faixa(g, k)
    return {"@type": "Offer", "priceCurrency": "EUR", "priceSpecification": {"@type": "UnitPriceSpecification", "minPrice": round(a, 2), "maxPrice": round(b, 2), "priceCurrency": "EUR", "unitText": "m²", "valueAddedTaxIncluded": False}}


# ---------------------------------------------------------------- fotografias reais
F = {
    "gaia_largo": ("g-foto-real-20260915-162859.webp", "Vila Nova de Gaia: terraço de 440 m² com acabamento mineral"),
    "gaia_rolo": ("g-telhado-real-04.webp", "Primeira camada de tela em cobertura plana"),
    "gaia_obra": ("g-foto-real-20260915-162840.webp", "Vila Nova de Gaia: terraço sobre garagem em obra nova"),
    "gaia_vista": ("g-foto-real-20260915-161005.webp", "Vila Nova de Gaia: vista geral da obra"),
    "gaia_juntas": ("g-foto-real-20260915-161418.webp", "Vila Nova de Gaia: sobreposição das faixas de tela"),
    "gaia_remate": ("g-foto-real-20260915-161929.webp", "Vila Nova de Gaia: remate junto à platibanda"),
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
FAQ_IVA = ("Os preços têm IVA?", IVA_LONGO)
FAQ_ZONA = ("Em que zonas trabalham?", "A partir de Sobral de Monte Agraço, nos distritos de Lisboa, Santarém, Setúbal e Leiria. Outras zonas mediante confirmação.")
LINKS_SERV = [("/coberturas-planas/", "Coberturas planas"), ("/terracos/", "Terraços"), ("/paredes/", "Caves e paredes enterradas"), ("/tela-asfaltica/", "Tela asfáltica"),
              ("/impermeabilizacao-condominios/", "Condomínios"), ("/empresas/", "Construtoras"), ("/precos-impermeabilizacao/", "Preços por m²"), ("/obras/", "Obras reais"), ("/guias/", "Guias")]
PRECOS_TELA = [("material", "tela_1"), ("material", "tela_2"), ("remocao", "tela_antiga"), ("suporte", "degradado"), ("suporte", "pendentes"), ("acesso", "escadas")]
PRECOS_TERRACO = [("material", "tela_1"), ("material", "tela_2"), ("material", "membrana_liquida"), ("remocao", "tela_antiga"), ("remocao", "sobre_ceramico"), ("suporte", "degradado"), ("suporte", "pendentes"), ("acesso", "escadas")]
PRECOS_MO = [("mo", "tela_1"), ("mo", "tela_2")]
PRECOS_TODOS = PRECOS_TERRACO[:3] + PRECOS_MO + [("material", "cimenticia")] + PRECOS_TERRACO[3:] + [("isolamento", "xps"), ("acabamento", "protecao_pesada")]

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
        precos=[("material", "tela_1"), ("material", "tela_2"), ("mo", "tela_1"), ("material", "cimenticia"), ("suporte", "degradado")],
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
                ("O que faz descer", "Áreas grandes e superfícies em bom estado."), ("IVA", IVA_CURTO)],
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
        servico="Impermeabilização de paredes", oferta=("material", "membrana_liquida")),
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
                ("Preços sem IVA", "Mostramos sempre o valor sem IVA, o que conta para a sua empresa."), ("Obras grandes", "Já executámos mais de 3.000 m² numa só obra.")],
        texto=["Envie as medições, a planta ou o mapa de quantidades e a data prevista. Respondemos com preço por m², o que está incluído e a disponibilidade.",
               "Procuramos parcerias com construtoras na região de Lisboa e Oeste: proposta rápida, preço por m² claro e cumprimento do planeamento da obra."],
        precos=PRECOS_TELA[:2] + PRECOS_MO + [("material", "membrana_liquida")], faq=[("Como é faturado o IVA?", IVA_LONGO), ("Fazem só a mão de obra?", "Sim, quando a construtora fornece o material. A calculadora tem a opção «só mão de obra» e a tabela mostra o preço por m²."), FAQ_MIN],
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
                ("Escala", "Acima de 200 m² o preço por m² desce ligeiramente."), ("IVA", IVA_CURTO)],
        texto=[f"Os preços são indicativos para obras a partir de {MIN} m², com acesso fácil, na zona de Lisboa e Oeste. Os preços estão na média do mercado e são iguais aos da calculadora."],
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
    "odivelas": dict(nome="Odivelas", nova=True,
        freg=["Odivelas", "Pontinha e Famões", "Póvoa de Santo Adrião e Olival Basto", "Ramada e Caneças"],
        fatores=[("Prédios e condomínios", "Terraços de cobertura de prédios em Odivelas, Póvoa de Santo Adrião e Ramada."), ("Caves e garagens", "Garagens e caves de condomínios, onde a água entra por paredes enterradas e juntas.")]),
    "amadora": dict(nome="Amadora", em="na", nova=True,
        freg=["Águas Livres", "Alfragide", "Encosta do Sol", "Falagueira-Venda Nova", "Mina de Água", "Venteira"],
        fatores=[("Prédios e condomínios", "Concelho muito urbano: sobretudo terraços de cobertura de prédios e garagens de condomínios."), ("Comércio e serviços", "Coberturas planas de edifícios de comércio e serviços, por exemplo em Alfragide.")]),
    "lourinha": dict(nome="Lourinhã", em="na", nova=True,
        freg=["Lourinhã e Atalaia", "Miragaia e Marteleira", "Moita dos Ferreiros", "Reguengo Grande", "Ribamar", "Santa Bárbara", "São Bartolomeu dos Galegos e Moledo", "Vimeiro"],
        fatores=[("Perto do mar", "Em Ribamar e na costa, o vento e a maresia desgastam mais depressa as telas expostas: o acabamento mineral protege-as."), ("Armazéns agrícolas", "Coberturas planas de armazéns e pavilhões agrícolas com grandes áreas.")]),
    "cadaval": dict(nome="Cadaval", em="no", nova=True,
        freg=["Alguber", "Cadaval e Pêro Moniz", "Lamas e Cercal", "Painho e Figueiros", "Peral", "Vermelha", "Vilar"],
        fatores=[("Armazéns e pavilhões", "Coberturas planas de armazéns e pavilhões agrícolas com grandes áreas."), ("Chuva com vento", "No Oeste a chuva vem batida pelo vento e entra sobretudo por remates, platibandas e soleiras.")]),
    "lisboa": dict(nome="Lisboa", freg=[],
        fatores=[("Edifícios antigos", "Terraços de cobertura com várias camadas antigas: muitas vezes é preciso remover antes de impermeabilizar."), ("Logística na cidade", "Acesso, estacionamento e licença de ocupação da via pública quando há contentor ou andaime.")]),
}
FOTOS_LOCAL = [["gaia_largo", "cobertura_mineral", "terraco_claraboia"], ["gaia_caso", "parede_imperalum", "gaia_rolo"], ["terraco_grua", "gaia_juntas", "aroeira"]]
for i, (slug, d) in enumerate(LOCAIS.items()):
    n = d["nome"]
    em = d.get("em", "em")  # "na Amadora", "no Cadaval"
    PAGINAS["impermeabilizacao-" + slug] = dict(
        titulo=f"Impermeabilização {em} {n}: Coberturas e Terraços | ImpermeabilizaPro",
        desc=f"Impermeabilização de coberturas planas, terraços e caves {em} {n}, para construtoras, condomínios e empresas. A partir de {MIN} m². Veja o preço por m².",
        eyebrow=f"IMPERMEABILIZAÇÃO · {n.upper()}", h1=f"Impermeabilização {em} {n}",
        sub=f"Coberturas planas, terraços e caves {em} {n}, para construtoras, condomínios e empresas. Obras a partir de {MIN} m².",
        sup=None, fotos=d.get("fotos", FOTOS_LOCAL[i % 3]), local=d,
        inclui=[(t, x) for t, x in d["fatores"]] + [("Preço por m² na hora", "Use a calculadora ou envie fotografias pelo WhatsApp.")],
        texto=[], precos=PRECOS_TELA[:3],
        faq=[(f"Fazem obras de impermeabilização {em} {n}?", f"Sim. Trabalhamos a partir de Sobral de Monte Agraço e fazemos obras {em} {n}."), FAQ_MIN, FAQ_IVA],
        servico=f"Impermeabilização {em} {n}", oferta=("material", "tela_2"), area=n)


# ---------------------------------------------------------------- HTML
def figura(k):
    img, cap = F[k]
    w, h = (1200, 675) if img.startswith("caso-") else (600, 450)
    ss = f' srcset="/assets/{img.replace(".webp", "-600.webp")} 600w, /assets/{img} 1200w" sizes="(max-width: 620px) 100vw, 40vw"' if img.startswith("caso-") else ""
    return f'<figure><img src="/assets/{img}"{ss} alt="{e(cap)}" width="{w}" height="{h}" loading="lazy"><figcaption>{e(cap)}</figcaption></figure>'


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
                f'<a class="btn outline big" href="tel:+351930446198" data-track="phone_calculadora">Ligar</a><a class="btn outline big calc-email" id="calcEmail" href="mailto:proimpermeabiliza@gmail.com">Enviar por email (com plantas)</a></div><p class="calc-legal">Estimativa indicativa, não é orçamento. O WhatsApp abre com os dados preenchidos; só nos chega quando carregar em Enviar.</p>'
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
    if com_fonte(p["precos"]):
        precos = (f'<section class="h-sec soft" id="precos"><div class="wrap"><h2>Preços de referência por m²</h2><p class="h-lead">Material e mão de obra, para obras a partir de <span data-minimo-obra>{MIN}</span> m² com acesso fácil. Preço médio de mercado, claro desde o primeiro contacto.</p>'
                  f'{tabela_precos(p["precos"])}<p class="calc-legal">Valores indicativos, não são orçamento. A calculadora junta os acréscimos e o desconto por área. Atualizado em {HOJE}.</p></div></section>')
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{minimo_span(a)}</p></details>" for q, a in p["faq"])
    links = "".join(f'<a href="{u}">{e(t)}</a>' for u, t in LINKS_SERV if u != f"/{slug}/")
    zonas = "".join(f'<a href="/impermeabilizacao-{s}/">{e(d["nome"])}</a>' for s, d in LOCAIS.items() if f"impermeabilizacao-{s}" != slug)
    ordem_precos_topo = p.get("precos_topo")
    corpo = (f'<section class="h-hero slim" id="pedido"><img src="/assets/foto-real-20260915-162914-1600.webp" srcset="/assets/foto-real-20260915-162914-800.webp 800w, /assets/foto-real-20260915-162914-1600.webp 1600w" sizes="100vw" alt="" width="1920" height="1080" fetchpriority="high">'
             f'<div class="wrap h-hero-in"><div><p class="h-crumbs"><a href="/">Início</a> › {e(p["h1"])}</p><p class="h-eyebrow">{e(p["eyebrow"])}</p><h1>{e(p["h1"])}</h1><p class="h-sub">{minimo_span(p["sub"])}</p>'
             f'<ul class="h-chips"><li>Obras a partir de <span data-minimo-obra>{MIN}</span> m²</li><li>Preço claro por m²</li><li>Fotografias reais</li></ul>'
             f'<p>Prefere falar? <a class="h-tel" href="tel:+351930446198" data-track="phone_hero">930 446 198</a> · Vinícius Nascimento</p>'
             + ('<p><a class="h-tel" href="/assets/apresentacao-impermeabilizapro.pdf" download>Descarregar apresentação (PDF, 4 páginas)</a></p>' if slug in ("empresas", "impermeabilizacao-condominios") else "")
             + f'</div>{calc}</div></section>\n')
    corpo += (precos if ordem_precos_topo else sec_fotos)
    corpo += f'<section class="h-sec{" soft" if not ordem_precos_topo else ""}"><div class="wrap"><h2>{"O que inclui" if not p.get("local") else "Em " + e(p["local"]["nome"])}</h2><ul class="h-inclui">{inclui}</ul>'
    corpo += f'<div class="h-texto" style="margin-top:18px">{texto}{local}</div></div></section>\n'
    corpo += (sec_fotos if ordem_precos_topo else precos)
    corpo += f'<section class="h-sec h-faq" id="faq"><div class="wrap narrow"><h2>Perguntas frequentes</h2>{faq}</div></section>\n'
    corpo += (f'<section class="h-sec soft"><div class="wrap"><div class="h-cta"><div><h2>Tem uma obra a partir de <span data-minimo-obra>{MIN}</span> m²?</h2><p>Envie medidas e fotografias. Respondemos com preço por m² e total.</p></div>'
              f'<a class="btn whatsapp big wa-direct" data-placement="cta_final" href="{wa}" target="_blank" rel="noopener noreferrer">Pedir proposta pelo WhatsApp</a></div>'
              f'<h2 style="margin-top:28px;font-size:1.2rem">Outros serviços</h2><div class="h-links">{links}</div><h2 style="margin-top:20px;font-size:1.2rem">Zonas</h2><div class="h-links">{zonas}</div></div></section>')
    modulo = '<script type="module" src="/calculadora/widget.mjs?v=20261113-12"></script>' if 'data-calc ' in calc or 'data-calc>' in calc else ""
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
<link rel="stylesheet" href="/style.css?v=20261113-limpo">
<link rel="stylesheet" href="/calculadora/calc.css?v=20261113-8">
<link rel="stylesheet" href="/assets/b2b.css?v=20261113-6">
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
             f'<p class="h-lead">Material e mão de obra, para obras a partir de <span data-minimo-obra>{MIN}</span> m² com acesso fácil. Preço médio de mercado, claro desde o primeiro contacto.</p>'
             f'{tabela_precos(PRECOS_TERRACO[:3] + [("remocao", "tela_antiga"), ("suporte", "degradado"), ("acesso", "escadas")])}'
             f'<p style="margin-top:14px"><a class="btn whatsapp big" href="/precos-impermeabilizacao/">Ver todos os preços</a></p></div></section>\n<!-- precos-referencia:fim -->')
    s = re.sub(r"<!-- precos-referencia:inicio -->.*?<!-- precos-referencia:fim -->", bloco, s, flags=re.S)
    p.write_text(s, encoding="utf-8")


def sitemap():
    urls = ["", "calculadora/"] + [f"{s}/" for s in PAGINAS] + ["obras/"] + [f"obras/{s}/" for s in OBRAS] + ["guias/"] + [f"guias/{s}/" for s in GUIAS]
    corpo = "".join(f"  <url><loc>{SITE}/{u}</loc><lastmod>{HOJE}</lastmod></url>\n" for u in urls)
    (RAIZ / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{corpo}</urlset>\n', encoding="utf-8")


def llms():
    linhas = [f"- {linha(g, k)['descricao']}: {n0(faixa(g, k)[0])}–{n0(faixa(g, k)[1])} €/m² sem IVA" + (" (material e mão de obra)" if g == "material" else (" (sem material)" if g == "mo" else " (acréscimo)")) for g, k in com_fonte(PRECOS_TODOS)]
    txt = f"""# ImpermeabilizaPro

> Impermeabilização de coberturas planas, terraços, caves e paredes enterradas para construtoras, condomínios e empresas, em Portugal (distritos de Lisboa, Santarém, Setúbal e Leiria). Base em Sobral de Monte Agraço. Responsável: Vinícius Nascimento (5 anos de experiência). Obras a partir de {MIN} m².

## Factos
- Serviços: coberturas planas, terraços, caves e paredes enterradas, aplicação de tela asfáltica (uma ou duas camadas), membranas líquidas e cimentícias, subempreitada para construtoras. Casas de banho: serviço à parte.
- Não faz: pequenas reparações, telhados de telha ou inclinados, trabalhos em grande altura.
- Mínimo de obra: {MIN} m² em coberturas e áreas planas.
- Obras reais: Aroeira (mais de 3.000 m² de paredes enterradas, tela Imperalum), Vila Nova de Gaia (terraço sobre garagem, 440 m², duas camadas), Ericeira (terraço de cobertura, cerca de 200 m²).
- IVA: {IVA_LONGO}
- Contacto: +351 930 446 198 (telefone e WhatsApp), proimpermeabiliza@gmail.com.

## Preços indicativos (atualizado em {HOJE}, obras a partir de {MIN} m², acesso fácil)
""" + "\n".join(linhas) + f"""
- Áreas maiores têm preço por m² ligeiramente mais baixo (a partir de 200 m², 500 m² e 1000 m²).

## Páginas
- [Calculadora de preço por m²]({SITE}/calculadora/)
- [Preços de impermeabilização por m²]({SITE}/precos-impermeabilizacao/)
""" + "\n".join(f"- [{p['h1']}]({SITE}/{s}/)" for s, p in PAGINAS.items() if s != "precos-impermeabilizacao") + "\n\n## Obras reais\n" + "\n".join(f"- [{a['h1']}]({SITE}/obras/{s}/): " + "; ".join(f"{k}: {v}" for k, v in a["ficha"]) for s, a in OBRAS.items()) + "\n\n## Guias\n" + "\n".join(f"- [{a['h1']}]({SITE}/guias/{s}/): {a['resumo']}" for s, a in GUIAS.items()) + "\n"
    (RAIZ / "llms.txt").write_text(txt, encoding="utf-8")



# ---------------------------------------------------------------- obras reais e guias
OBRAS = {
    "aroeira-paredes-enterradas": dict(
        titulo="Obra: Paredes Enterradas na Aroeira, mais de 3.000 m² | ImpermeabilizaPro",
        desc="Impermeabilização de mais de 3.000 m² de paredes enterradas na Aroeira, com tela Imperalum com armadura em poliéster.",
        h1="Paredes enterradas na Aroeira", img="caso-aroeira-3000m2.webp",
        ficha=[("Local", "Aroeira"), ("Área", "Mais de 3.000 m²"), ("Tipo", "Paredes enterradas"), ("Sistema", "Tela Imperalum com armadura em poliéster"), ("Estado", "Em execução")],
        texto=["Obra nova com grande área de paredes em contacto com o terreno. A tela é aplicada antes do aterro, no planeamento da construtora.",
               "Numa parede enterrada, a água vem do terreno e exerce pressão: a impermeabilização tem de ser contínua, bem soldada nas sobreposições e rematada junto à fundação."],
        galeria=["parede_maquina", "parede_imperalum", "parede_fundacao"], sup="cave"),
    "gaia-terraco-garagem-440m2": dict(
        titulo="Obra: Terraço sobre Garagem em Vila Nova de Gaia, 440 m² | ImpermeabilizaPro",
        desc="Impermeabilização de um terraço sobre garagem com 440 m² em Vila Nova de Gaia: duas camadas de tela e acabamento mineral em xisto.",
        h1="Terraço sobre garagem em Vila Nova de Gaia", img="caso-gaia-440m2.webp",
        ficha=[("Local", "Vila Nova de Gaia"), ("Área", "440 m²"), ("Tipo", "Terraço sobre garagem"), ("Sistema", "Duas camadas de tela asfáltica"), ("Acabamento", "Mineral em xisto")],
        texto=["Um terraço sobre garagem tem de aguentar água parada, variações de temperatura e, muitas vezes, passagem. Por isso usámos duas camadas de tela.",
               "A segunda camada tem acabamento mineral em xisto, que protege a tela do sol quando fica à vista."],
        galeria=["gaia_largo", "gaia_obra", "gaia_vista", "gaia_juntas", "gaia_remate"], galeria_titulo="Fotografias da obra", sup="terraco"),
    "ericeira-terraco-cobertura-200m2": dict(
        titulo="Obra: Terraço de Cobertura na Ericeira, cerca de 200 m² | ImpermeabilizaPro",
        desc="Impermeabilização de um terraço de cobertura com cerca de 200 m² na Ericeira (Mafra): tela com fibra de vidro e acabamento mineral em xisto.",
        h1="Terraço de cobertura na Ericeira", img="caso-ericeira-200m2.webp",
        ficha=[("Local", "Ericeira (Mafra)"), ("Área", "Cerca de 200 m²"), ("Tipo", "Terraço de cobertura"), ("Sistema", "Tela com armadura em fibra de vidro"), ("Acabamento", "Mineral em xisto")],
        texto=["Junto ao mar, o vento e a maresia desgastam mais depressa as superfícies expostas. O acabamento mineral protege a tela do sol e do desgaste.",
               "Num terraço comprido com platibandas, os remates laterais são a parte mais importante: é por aí que a água entra mais vezes."],
        galeria=["cobertura_remates", "cobertura_ralo", "murete"], sup="terraco"),
}

GUIAS = {
    "tela-asfaltica-ou-membrana-liquida": dict(
        titulo="Tela Asfáltica ou Membrana Líquida: Qual Escolher? | ImpermeabilizaPro",
        desc="Tela asfáltica ou membrana líquida numa cobertura plana ou terraço: diferenças, quando usar cada uma e preço por m².",
        h1="Tela asfáltica ou membrana líquida: qual escolher?", sup="cobertura_plana",
        resumo="Em coberturas planas e terraços grandes, a tela asfáltica em duas camadas é normalmente a opção mais económica e robusta. A membrana líquida compensa quando há muitos remates, equipamentos ou formas irregulares.",
        secoes=[("Tela asfáltica", ["Rolos de betume modificado com armadura (poliéster ou fibra de vidro), soldados a maçarico, em uma ou duas camadas.", "Boa em áreas grandes e regulares. Com acabamento mineral pode ficar à vista; sem acabamento, precisa de proteção."]),
                ("Membrana líquida", ["Produto aplicado a rolo, trincha ou projeção, que forma uma película contínua sem juntas.", "Boa em superfícies com muitos tubos, maciços, caleiras ou claraboias, onde soldar tela à volta de cada ponto é demorado."]),
                ("O que pesa mais do que o material", ["Preparação da superfície, remoção do sistema antigo, pendentes e remates. Um bom material mal rematado infiltra.", "A durabilidade depende do produto concreto: peça sempre a ficha técnica do sistema proposto."])],
        precos=[("material", "tela_1"), ("material", "tela_2"), ("material", "membrana_liquida")],
        faq=[("Posso aplicar membrana líquida sobre tela antiga?", "Depende do estado e da compatibilidade dos produtos. Se a tela antiga estiver descolada ou com bolhas, tem de ser removida."), ("Qual dura mais?", "Depende do produto, da espessura e da exposição. Compare as fichas técnicas dos sistemas propostos.")]),
    "impermeabilizar-terraco-condominio": dict(
        titulo="Impermeabilizar o Terraço do Condomínio: Quem Paga e Como Aprovar",
        desc="O terraço de cobertura é parte comum do prédio. Quem paga a impermeabilização, como aprovar em assembleia e o que pedir nas propostas.",
        h1="Impermeabilizar o terraço do condomínio: quem paga e como aprovar", sup="terraco", cliente="condominio",
        resumo="O terraço de cobertura é parte comum do prédio, mesmo quando só uma fração o usa. A obra é normalmente decidida em assembleia e paga pelos condóminos na proporção da permilagem, com exceções.",
        secoes=[("O terraço é parte comum", ["O Código Civil considera partes comuns «o telhado ou os terraços de cobertura, ainda que destinados ao uso de qualquer fração» (art. 1421.º, n.º 1, alínea b))."]),
                ("Quem paga", ["As despesas de conservação das partes comuns são pagas pelos condóminos na proporção do valor das frações (art. 1424.º, n.º 1).", "Há regras próprias para partes comuns que servem só alguns condóminos (art. 1424.º, n.º 3). Em caso de dúvida, confirme com a administração ou um jurista."]),
                ("Urgências", ["Reparações indispensáveis e urgentes podem ser feitas por iniciativa de qualquer condómino quando o administrador não o faça (art. 1427.º)."]),
                ("Como preparar a assembleia", ["Fotografias e descrição das infiltrações.", "Duas ou três propostas comparáveis: mesma área, mesmo sistema, mesmos remates.", "Preço por m² e total com IVA, prazo, condições de pagamento e garantia escrita."])],
        precos=[("material", "tela_2"), ("remocao", "tela_antiga"), ("acesso", "escadas")],
        faq=[("O condómino do último andar paga tudo?", "Em regra não: o terraço de cobertura é parte comum. Há exceções para partes de uso exclusivo; confirme com a administração."), ("Que IVA se aplica?", "A taxa legal: 23%, ou 6% em obras de reparação em habitação quando a lei o permite.")]),
    "comparar-orcamentos-impermeabilizacao": dict(
        titulo="Como Comparar Orçamentos de Impermeabilização (Checklist)",
        desc="O que deve constar num orçamento de impermeabilização para comparar propostas: área, sistema, remoção, remates, acabamento, prazo, garantia e IVA.",
        h1="Como comparar orçamentos de impermeabilização", sup=None,
        resumo="Dois orçamentos só são comparáveis se tiverem a mesma área, o mesmo sistema e os mesmos trabalhos incluídos. Use esta lista antes de decidir.",
        secoes=[("O que tem de estar escrito", ["Área medida em m² e como foi medida.", "Sistema e produto: tela de uma ou duas camadas, membrana líquida ou cimentícia, com marca e ficha técnica.", "Preparação: limpeza, regularização, primário e remoção do sistema antigo.", "Ralos, remates, platibandas, soleiras e juntas incluídos.", "Acabamento: mineral, pintura UV, proteção pesada ou pavimento.", "Prazo, condições de pagamento, garantia escrita e IVA."]),
                ("Sinais de alerta", ["Preço por m² muito abaixo sem explicar a preparação.", "Proposta sem marca nem sistema.", "Remates e ralos «a orçamentar depois»."])],
        precos=[("material", "tela_1"), ("material", "tela_2"), ("material", "membrana_liquida")],
        faq=[("Porque é que os preços variam tanto?", "Sobretudo pela preparação, remoção do sistema antigo, remates e acessos, não tanto pelo material."), ("Vale a pena a proposta mais barata?", "Só se incluir o mesmo que as outras. Compare linha a linha.")]),
    "paredes-enterradas-obra-nova": dict(
        titulo="Impermeabilização de Paredes Enterradas em Obra Nova: Quando e Como",
        desc="Quando impermeabilizar paredes enterradas numa obra nova, que sistema usar e o que coordenar com a construtora antes do aterro.",
        h1="Paredes enterradas em obra nova: quando e como impermeabilizar", sup="cave", cliente="empresa",
        resumo="A impermeabilização de paredes enterradas faz-se pelo lado de fora, depois da betonagem e antes do aterro. Depois do aterro, a reparação é muito mais cara.",
        secoes=[("Quando", ["Com as paredes betonadas e secas, antes do aterro.", "Combinar com a construtora a sequência: impermeabilização, proteção e drenagem, aterro."]),
                ("Como", ["Limpeza e regularização da parede, primário e tela asfáltica com armadura em poliéster, soldada a maçarico, com sobreposições.", "Remate no encontro com a fundação e nas juntas de betonagem.", "Proteção da tela antes do aterro, para não ser danificada."]),
                ("Drenagem", ["Em terrenos com água, a impermeabilização é complementada por drenagem junto à fundação, definida no projeto."])],
        precos=[("material", "tela_1"), ("material", "tela_2")],
        faq=[("Uma ou duas camadas?", "Depende do projeto e da presença de água no terreno. Em zonas com água sob pressão usa-se normalmente sistema reforçado."), ("Fazem só a mão de obra?", "Sim, quando a construtora fornece o material.")]),
}

GUIAS.update({
    "coberturas-armazens-pavilhoes": dict(
        titulo="Impermeabilização de Coberturas de Armazéns e Pavilhões | ImpermeabilizaPro",
        desc="Como impermeabilizar a cobertura plana de um armazém ou pavilhão sem parar a atividade: sistema, fases, escoamento e preço por m².",
        h1="Coberturas planas de armazéns e pavilhões: como impermeabilizar", sup="cobertura_plana", cliente="empresa",
        resumo="Em coberturas planas de grande área, o que mais conta é o escoamento (pendentes, caleiras e ralos) e fazer a obra por fases, para o armazém continuar a trabalhar. A tela asfáltica em duas camadas é a solução mais usada.",
        secoes=[("Antes de começar", ["Ver por onde entra a água: ralos entupidos, caleiras, juntas de dilatação e encontros com platibandas são os pontos habituais.", "Medir a área e confirmar o acesso à cobertura (escada fixa ou acesso interior). Não fazemos trabalhos em grande altura."]),
                ("Por fases, sem parar a atividade", ["A cobertura é dividida em zonas. Cada zona fica impermeabilizada no mesmo dia ou protegida ao fim do dia, para não entrar água durante a obra.", "Os trabalhos são marcados para dias secos."]),
                ("Escoamento", ["Água parada estraga qualquer sistema. Corrigir pendentes e aumentar ou desentupir ralos e caleiras faz parte da solução."]),
                ("Sistema", ["Normalmente duas camadas de tela asfáltica, com a segunda autoprotegida com acabamento mineral. Em zonas com muitos equipamentos, membrana líquida à volta dos pontos difíceis."])],
        precos=[("material", "tela_2"), ("mo", "tela_2"), ("suporte", "pendentes")],
        faq=[("É preciso parar o armazém?", "Não. Trabalhamos por zonas e protegemos cada zona ao fim do dia."), ("Fazem coberturas de chapa?", "Fazemos coberturas planas. Telhados inclinados, de telha ou chapa, não fazemos.")]),
    "planear-impermeabilizacao-obra-nova": dict(
        titulo="Planear a Impermeabilização numa Obra Nova (para Construtoras)",
        desc="Quando entra a impermeabilização no planeamento de uma obra nova, o que enviar para a proposta e como coordenar com as outras especialidades.",
        h1="Como planear a impermeabilização numa obra nova", sup="terraco", cliente="empresa",
        resumo="A impermeabilização tem momentos certos no planeamento: paredes enterradas antes do aterro, coberturas e terraços depois das lajes e antes dos pavimentos e caixilharias finais. Planear cedo evita refazer trabalho.",
        secoes=[("Quando entra no planeamento", ["Paredes enterradas: depois da betonagem e antes do aterro.", "Coberturas e terraços: depois das lajes e das pendentes, antes da proteção, do pavimento e dos remates de caixilharia."]),
                ("O que enviar para a proposta", ["Mapa de quantidades ou medições, plantas de cobertura e cortes, pormenores de remates (platibandas, soleiras, ralos) e a data prevista.", "Com isto respondemos com preço por m², total e o que está incluído; com material ou só mão de obra."]),
                ("Coordenação com as outras especialidades", ["Ralos, tubos e passagens colocados antes da impermeabilização.", "Soleiras e caixilharias com altura suficiente para o remate subir acima do pavimento acabado.", "Evitar furar a impermeabilização depois de feita; se for preciso, avisar para rematar."]),
                ("Verificar antes de tapar", ["É prática comum fazer um teste de alagamento (encher a cobertura com água e verificar) antes da proteção ou do pavimento."])],
        precos=[("material", "tela_2"), ("mo", "tela_1"), ("mo", "tela_2")],
        faq=[("Com quanto tempo de antecedência devo pedir?", "Assim que houver medições. Quanto mais cedo, mais fácil encaixar as datas no planeamento da obra."), ("Fazem só a mão de obra?", "Sim, quando a construtora fornece o material.")]),
    "manutencao-terraco-condominio": dict(
        titulo="Manutenção do Terraço do Condomínio: Evitar Infiltrações",
        desc="O que a administração de um condomínio deve verificar no terraço de cobertura para evitar infiltrações, e quando é altura de renovar a impermeabilização.",
        h1="Manutenção do terraço do condomínio: o que verificar", sup="terraco", cliente="condominio",
        resumo="A maior parte das infiltrações em terraços de cobertura começa em ralos entupidos e remates danificados. Uma verificação simples antes do outono e depois de tempestades evita muitas reparações.",
        secoes=[("O que verificar", ["Ralos e caleiras limpos, sem folhas nem terra.", "Remates junto às platibandas, muretes e soleiras: sem fissuras nem tela descolada.", "Água parada depois da chuva: indica pendentes a corrigir.", "Plantas a crescer em juntas ou cantos: as raízes danificam a impermeabilização."]),
                ("Quando fazer", ["Antes do outono e depois de tempestades fortes. Registar com fotografias, para comparar de ano para ano."]),
                ("Sinais de que é preciso renovar", ["Manchas no teto do último andar depois da chuva, bolhas ou tela descolada em várias zonas, ou reparações repetidas no mesmo sítio."]),
                ("Cuidados", ["Não furar o terraço para fixar antenas, toldos ou equipamentos sem rematar a impermeabilização.", "Não usar ferramentas cortantes na limpeza."])],
        precos=[("material", "tela_2"), ("remocao", "tela_antiga"), ("acesso", "escadas")],
        faq=[("A limpeza dos ralos é connosco?", "Não fazemos manutenções pequenas. Fazemos a renovação da impermeabilização a partir de 100 m²."), ("Quem paga a renovação?", "Em regra os condóminos, na proporção da permilagem, porque o terraço de cobertura é parte comum. Veja o guia sobre o terraço do condomínio.")]),
})


def pagina_artigo(caminho, a, tipo):
    url = f"{SITE}/{caminho}/"
    crumbs_nome, crumbs_url = ("Obras", "/obras/") if tipo == "obra" else ("Guias", "/guias/")
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Início", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": crumbs_nome, "item": SITE + crumbs_url},
        {"@type": "ListItem", "position": 3, "name": a["h1"], "item": url}]}
    lds = [crumbs]
    corpo = ""
    if tipo == "obra":
        lds.append({"@context": "https://schema.org", "@type": "WebPage", "name": a["h1"], "url": url, "description": a["desc"], "image": f"{SITE}/assets/{a['img']}",
                    "about": {"@type": "Service", "serviceType": "Impermeabilização", "provider": {"@id": NEGOCIO_ID}}})
        ficha = "".join(f"<tr><th scope=\"row\">{e(k)}</th><td>{e(v)}</td></tr>" for k, v in a["ficha"])
        corpo += (f'<section class="h-sec"><div class="wrap h-obra"><figure class="h-caso"><img src="/assets/{a["img"]}" alt="{e(a["h1"])}" srcset="/assets/{a["img"].replace(".webp", "-600.webp")} 600w, /assets/{a["img"]} 1200w" sizes="(max-width: 980px) 100vw, 55vw" width="1200" height="675"></figure>'
                  f'<div><h2>Ficha da obra</h2><table class="price-table h-ficha"><tbody>{ficha}</tbody></table><div class="h-texto">{"".join(f"<p>{e(t)}</p>" for t in a["texto"])}</div></div></div></section>')
        corpo += (f'<section class="h-sec soft"><div class="wrap"><h2>{e(a.get("galeria_titulo", "Outras fotografias de obras semelhantes"))}</h2><div class="h-galeria h-galeria-{len(a["galeria"])}">{"".join(figura(k) for k in a["galeria"])}</div></div></section>')
    else:
        lds.append({"@context": "https://schema.org", "@type": "Article", "headline": a["h1"], "description": a["desc"], "url": url, "inLanguage": "pt-PT", "dateModified": HOJE,
                    "author": {"@type": "Person", "name": "Vinícius Nascimento"}, "publisher": {"@id": NEGOCIO_ID}, "image": f"{SITE}/assets/foto-real-20260915-162914.jpeg"})
        lds.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in a["faq"]]})
        sec = "".join(f'<h2>{e(t)}</h2>' + (f'<ul>{"".join(f"<li>{e(x)}</li>" for x in ps)}</ul>' if len(ps) > 1 else f"<p>{e(ps[0])}</p>") for t, ps in a["secoes"])
        tab = f'<h2>Preço por m² (referência)</h2>{tabela_precos(a["precos"])}' if com_fonte(a["precos"]) else ""
        faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(r)}</p></details>" for q, r in a["faq"])
        corpo += (f'<section class="h-sec"><div class="wrap narrow h-artigo"><p class="h-resumo"><strong>Resumo:</strong> {e(a["resumo"])}</p>{sec}{tab}'
                  f'<p class="calc-legal">Atualizado em {HOJE}. Informação geral; não substitui o projeto nem aconselhamento jurídico.</p></div></section>'
                  f'<section class="h-sec soft h-faq"><div class="wrap narrow"><h2>Perguntas frequentes</h2>{faq}</div></section>')
    attrs = (f' data-superficie="{a["sup"]}"' if a.get("sup") else "") + (f' data-cliente="{a["cliente"]}"' if a.get("cliente") else "")
    calc = (f'<section class="h-sec" id="pedido"><div class="wrap"><div class="calc" data-calc data-modo="rapido"{attrs} style="max-width:760px;margin:0 auto"><h2>{"Tem uma obra semelhante? Veja o preço por m²" if tipo == "obra" else "Quanto custaria na sua obra?"}</h2>'
            f'<form data-calc-form novalidate><p class="calc-vazio">A carregar a calculadora…</p></form><div class="calc-res" data-calc-result aria-live="polite"></div>'
            f'<div class="calc-acoes" id="calcAcoes" hidden><a class="btn whatsapp big" id="calcWa" data-placement="calculadora_{tipo}" href="https://wa.me/351930446198" target="_blank" rel="noopener noreferrer">Pedir proposta pelo WhatsApp</a>'
            f'<a class="btn outline big" href="tel:+351930446198" data-track="phone_calculadora">Ligar</a><a class="btn outline big calc-email" id="calcEmail" href="mailto:proimpermeabiliza@gmail.com">Enviar por email (com plantas)</a></div>'
            f'<p class="calc-legal">Estimativa indicativa, não é orçamento. O WhatsApp abre com os dados preenchidos; só nos chega quando carregar em Enviar.</p></div></div></section>')
    outros = OBRAS if tipo == "obra" else GUIAS
    links = "".join(f'<a href="/{"obras" if tipo == "obra" else "guias"}/{s}/">{e(o["h1"])}</a>' for s, o in outros.items() if f"/{s}" not in caminho)
    corpo += calc + f'<section class="h-sec soft"><div class="wrap"><h2 style="font-size:1.2rem">{"Outras obras" if tipo == "obra" else "Outros guias"}</h2><div class="h-links">{links}</div><h2 style="margin-top:20px;font-size:1.2rem">Serviços</h2><div class="h-links">{"".join(f"<a href=\"{u}\">{e(t)}</a>" for u, t in LINKS_SERV)}</div></div></section>'
    hero = (f'<section class="h-hero slim"><img src="/assets/foto-real-20260915-162914-1600.webp" srcset="/assets/foto-real-20260915-162914-800.webp 800w, /assets/foto-real-20260915-162914-1600.webp 1600w" sizes="100vw" alt="" width="1920" height="1080" fetchpriority="high">'
            f'<div class="wrap"><p class="h-crumbs"><a href="/">Início</a> › <a href="{crumbs_url}">{crumbs_nome}</a></p><p class="h-eyebrow">{"OBRA REAL" if tipo == "obra" else "GUIA"}</p><h1>{e(a["h1"])}</h1><p class="h-sub">{e(a["desc"])}</p>'
            f'<p><a class="btn whatsapp big" href="#pedido">Ver preço para a minha obra</a> <a class="h-tel" href="tel:+351930446198" data-track="phone_hero">930 446 198</a></p></div></section>')
    return cabeca(a["titulo"], a["desc"], url, lds) + f"<main id=\"conteudo\">\n{hero}\n{corpo}\n</main>\n<footer></footer>\n<script type=\"module\" src=\"/calculadora/widget.mjs?v=20261113-12\"></script>\n</body>\n</html>\n"


def pagina_indice(tipo):
    itens = OBRAS if tipo == "obra" else GUIAS
    base = "obras" if tipo == "obra" else "guias"
    h1 = "Obras reais" if tipo == "obra" else "Guias de impermeabilização"
    desc = ("Obras de impermeabilização realizadas: paredes enterradas, terraços e coberturas, com área, sistema e fotografias reais." if tipo == "obra"
            else "Guias práticos para construtoras e condomínios: escolher o sistema, comparar orçamentos, aprovar a obra em assembleia.")
    url = f"{SITE}/{base}/"
    cards = ""
    for s, a in itens.items():
        img = a.get("img") or "g-foto-real-20260915-162859.webp"
        w, h = (1200, 675) if img.startswith("caso-") else (600, 450)
        ss = f' srcset="/assets/{img.replace(".webp", "-600.webp")} 600w, /assets/{img} 1200w" sizes="(max-width: 620px) 100vw, 33vw"' if img.startswith("caso-") else ""
        cards += f'<a class="h-servico" href="/{base}/{s}/"><img src="/assets/{img}"{ss} alt="" width="{w}" height="{h}" loading="lazy"><div><strong>{e(a["h1"])}</strong><span>{e(a["desc"])}</span></div></a>'
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Início", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": h1, "item": url}]}
    corpo = (f'<section class="h-hero slim"><img src="/assets/foto-real-20260915-162914-1600.webp" srcset="/assets/foto-real-20260915-162914-800.webp 800w, /assets/foto-real-20260915-162914-1600.webp 1600w" sizes="100vw" alt="" width="1920" height="1080" fetchpriority="high">'
             f'<div class="wrap"><p class="h-crumbs"><a href="/">Início</a> › {h1}</p><h1>{h1}</h1><p class="h-sub">{e(desc)}</p></div></section>'
             f'<section class="h-sec"><div class="wrap"><div class="h-servicos h-servicos-3">{cards}</div><p style="margin-top:24px"><a class="btn whatsapp big" href="/calculadora/">Calcular o preço da minha obra</a></p></div></section>')
    return cabeca(f"{h1} | ImpermeabilizaPro", desc, url, [crumbs]) + f"<main id=\"conteudo\">\n{corpo}\n</main>\n<footer></footer>\n</body>\n</html>\n"


def cabeca(titulo, desc, url, lds, robots="index,follow,max-image-preview:large", extra_head=""):
    return f'''<!doctype html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{e(titulo)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">{extra_head}
<meta property="og:type" content="article"><meta property="og:locale" content="pt_PT"><meta property="og:url" content="{url}">
<meta property="og:title" content="{e(titulo)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE}/assets/foto-real-20260915-162914.jpeg"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0a2340">
<link rel="icon" href="/assets/logo-impermeabilizapro.webp" type="image/webp">
<link rel="preload" as="image" href="/assets/foto-real-20260915-162914-800.webp" imagesrcset="/assets/foto-real-20260915-162914-800.webp 800w, /assets/foto-real-20260915-162914-1600.webp 1600w" imagesizes="100vw">
<link rel="stylesheet" href="/style.css?v=20261113-limpo">
<link rel="stylesheet" href="/calculadora/calc.css?v=20261113-8">
<link rel="stylesheet" href="/assets/b2b.css?v=20261113-6">
{"".join(f'<script type="application/ld+json">{json.dumps(l, ensure_ascii=False)}</script>' for l in lds)}
</head>
<body class="pagina-b2b">
<header class="header"></header>
'''


def gerar_obras_guias():
    for tipo, itens, base in (("obra", OBRAS, "obras"), ("guia", GUIAS, "guias")):
        (RAIZ / base).mkdir(exist_ok=True)
        (RAIZ / base / "index.html").write_text(pagina_indice(tipo), encoding="utf-8")
        for s, a in itens.items():
            d = RAIZ / base / s
            d.mkdir(exist_ok=True)
            (d / "index.html").write_text(pagina_artigo(f"{base}/{s}", a, tipo), encoding="utf-8")


# ---------------------------------------------------------------- apresentação (HTML A4 → PDF com scripts/gerar_pdf.js)
def apresentacao():
    obras = "".join(
        f'<div class="ob"><img src="/assets/{a["img"]}" alt=""><div><h3>{e(a["h1"])}</h3><table>{"".join(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in a["ficha"])}</table></div></div>'
        for a in OBRAS.values())
    serv = [("g-obra-real-cobertura-02.webp", "Coberturas planas", "Edifícios, armazéns e pavilhões."), ("g-telhado-real-04.webp", "Terraços", "De cobertura, sobre garagens e de condomínios."),
            ("g-parede-real-01.webp", "Caves e paredes enterradas", "Obra nova, antes do aterro."), ("g-telhado-real-01.webp", "Tela asfáltica", "Uma ou duas camadas, acabamento mineral.")]
    servh = "".join(f'<div class="sv"><img src="/assets/{i}" alt=""><b>{e(t)}</b><span>{e(d)}</span></div>' for i, t, d in serv)
    html_ = f'''<!doctype html><html lang="pt-PT"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow">
<title>Apresentação ImpermeabilizaPro</title><link rel="canonical" href="{SITE}/apresentacao/">
<style>
@page{{size:A4;margin:0}}*{{box-sizing:border-box}}body{{margin:0;font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;color:#122943}}
.pg{{width:210mm;height:297mm;padding:16mm 15mm;position:relative;page-break-after:always;overflow:hidden}}
.capa{{color:#fff;padding:0}}.capa>img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}.capa::after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,#061a33e6,#0a2340b3 55%,#061a33f2)}}
.capa .in{{position:relative;z-index:1;padding:22mm 16mm;height:100%;display:flex;flex-direction:column}}
.logo{{display:flex;gap:10px;align-items:center;font-weight:800;font-size:20px}}.logo img{{width:48px;height:48px;border-radius:8px;background:#fff}}
h1{{font-size:38px;line-height:1.08;margin:auto 0 12px;letter-spacing:-.02em}}.capa p{{font-size:16px;color:#d7e7f3;max-width:150mm;line-height:1.5}}
.chips{{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 26px}}.chips span{{border:1px solid #ffffff55;border-radius:99px;padding:6px 12px;font-size:12px;font-weight:700}}
.ct{{font-size:15px;line-height:1.7}}.ct b{{font-size:20px}}
h2{{font-size:24px;margin:0 0 4px;color:#0a2340}}.lead{{color:#4a5e6f;margin:0 0 14px;font-size:13px}}
.svs{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}.sv{{border:1px solid #dce4eb;border-radius:10px;overflow:hidden;font-size:12px}}.sv img{{width:100%;height:38mm;object-fit:cover;display:block}}.sv b{{display:block;padding:7px 9px 0;font-size:14px}}.sv span{{display:block;padding:2px 9px 9px;color:#4a5e6f}}
.para{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:14px;font-size:12px}}.para div{{border-left:4px solid #0c7357;background:#f3f6f9;padding:8px 10px}}.para b{{display:block;font-size:13px}}
.nao{{margin-top:12px;font-size:12px;color:#4a5e6f}}
.ob{{display:grid;grid-template-columns:78mm 1fr;gap:10px;margin-bottom:10px;border:1px solid #dce4eb;border-radius:10px;overflow:hidden}}.ob img{{width:100%;height:50mm;object-fit:cover;display:block}}.ob h3{{font-size:15px;margin:8px 0 4px}}
.ob table{{font-size:11.5px;border-collapse:collapse}}.ob th{{text-align:left;color:#4a5e6f;padding:2px 8px 2px 0;font-weight:600}}.ob td{{padding:2px 0}}
.price-table{{width:100%;border-collapse:collapse;font-size:12px;margin:6px 0}}.price-table th,.price-table td{{padding:7px 8px;border-bottom:1px solid #e1e8ee;text-align:left}}.price-table thead th{{background:#0a2340;color:#fff}}.price-table small{{display:block;color:#5b6d7c;font-weight:400}}.sr-only{{display:none}}
.passos{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;font-size:12px;margin-top:10px}}.passos div{{background:#f3f6f9;border-radius:8px;padding:9px}}.passos b{{display:block;font-size:13px}}
.nota{{font-size:10.5px;color:#5b6d7c;line-height:1.45}}
.rod{{position:absolute;left:15mm;right:15mm;bottom:10mm;display:flex;justify-content:space-between;font-size:10.5px;color:#5b6d7c;border-top:1px solid #e1e8ee;padding-top:6px}}
.fim{{background:#0a2340;color:#fff;border-radius:12px;padding:14px 16px;margin-top:14px}}.fim b{{font-size:18px}}
</style></head><body>
<section class="pg capa"><img src="/assets/foto-real-20260915-162914-1600.webp" alt=""><div class="in">
<div class="logo"><img src="/assets/logo-impermeabilizapro.webp" alt="">ImpermeabilizaPro</div>
<h1>Impermeabilização de coberturas, terraços e caves para obras</h1>
<p>Para construtoras, condomínios e empresas nos distritos de Lisboa, Santarém, Setúbal e Leiria. Base em Sobral de Monte Agraço.</p>
<div class="chips"><span>Obras a partir de {MIN} m²</span><span>De {MIN} a mais de 3.000 m²</span><span>Com material ou só execução</span><span>Preço claro por m²</span></div>
<div class="ct">Vinícius Nascimento · 5 anos de experiência<br><b>930 446 198</b> (telefone e WhatsApp)<br>proimpermeabiliza@gmail.com · impermeabilizapro.pt</div></div></section>
<section class="pg"><h2>O que fazemos</h2><p class="lead">Coberturas e áreas planas a partir de {MIN} m². Subempreitada ou obra completa.</p><div class="svs">{servh}</div>
<div class="para"><div><b>Construtoras e empreiteiros</b>Subempreitada com material e mão de obra, ou só execução.</div><div><b>Condomínios e administrações</b>Proposta com preço por m² e total para a assembleia.</div><div><b>Empresas e armazéns</b>Coberturas planas de grande área.</div><div><b>Moradias com grandes áreas</b>Coberturas e terraços a partir de {MIN} m².</div></div>
<p class="nao">Não fazemos pequenas reparações, telhados de telha nem trabalhos em grande altura.</p><div class="rod"><span>ImpermeabilizaPro</span><span>930 446 198 · impermeabilizapro.pt</span></div></section>
<section class="pg"><h2>Obras reais</h2><p class="lead">Fotografias das nossas obras.</p>{obras}<div class="rod"><span>ImpermeabilizaPro</span><span>930 446 198 · impermeabilizapro.pt</span></div></section>
<section class="pg"><h2>Preços de referência por m²</h2><p class="lead">Material e mão de obra, obras a partir de {MIN} m² com acesso fácil. Preço médio de mercado, claro desde o primeiro contacto. Áreas maiores têm preço por m² ligeiramente mais baixo.</p>
{tabela_precos(PRECOS_TERRACO)}
<p class="nota">Valores indicativos ({HOJE}); não são orçamento. {e(IVA_LONGO)} O valor final é confirmado depois de vermos a obra.</p>
<h2 style="margin-top:14px">Como trabalhamos</h2><div class="passos"><div><b>1. Medições e fotografias</b>Planta, mapa de quantidades ou caderno de encargos.</div><div><b>2. Proposta</b>Solução, preço por m², total e o que está incluído.</div><div><b>3. Execução</b>Datas combinadas com o planeamento da obra.</div></div>
<div class="fim"><b>Peça uma proposta</b><br>930 446 198 (telefone e WhatsApp) · proimpermeabiliza@gmail.com<br>Calculadora de preço por m²: impermeabilizapro.pt/calculadora</div>
<div class="rod"><span>ImpermeabilizaPro</span><span>930 446 198 · impermeabilizapro.pt</span></div></section>
</body></html>'''
    # Imagens em JPEG leve (assets/pdf/) para o PDF não ficar pesado.
    html_ = re.sub(r'src="/assets/(?!logo)([^"]+)\.(webp|jpeg)"', r'src="/assets/pdf/\1.jpg"', html_)
    (RAIZ / "apresentacao").mkdir(exist_ok=True)
    (RAIZ / "apresentacao" / "index.html").write_text(html_, encoding="utf-8")


# ---------------------------------------------------------------- páginas legais e /telhados/
REVIEW_URL = "https://g.page/r/CSxqX6SG4QDvEBM/review"

PRIVACIDADE = [
    ("Quem trata os dados", [
        "ImpermeabilizaPro é o nome comercial de uma sociedade por quotas em constituição. Até ao registo da sociedade, o responsável pelo tratamento é Vinícius Nascimento. A denominação, o NIF e a sede da sociedade serão indicados aqui logo após o registo.",
        'Contacto para privacidade: <a href="mailto:proimpermeabiliza@gmail.com">proimpermeabiliza@gmail.com</a> · <a href="tel:+351930446198">930 446 198</a>.']),
    ("Calculadora de preço", [
        "As respostas à calculadora (tipo de cliente, superfície, área, localização, estado da superfície e outras) são usadas no seu navegador para calcular a estimativa. Não são enviadas para nenhuma base de dados do site.",
        "Se aceitar os cookies de medição, registamos apenas categorias de utilização: que a calculadora foi usada, o tipo de cliente, o tipo de superfície, o escalão de área (por exemplo, 200 a 499 m²), a zona e se a estimativa teve preço. Nunca registamos a localidade escrita, a área exata, o texto das mensagens nem dados de contacto."]),
    ("WhatsApp, email e telefone", [
        "Os botões de WhatsApp e de email abrem a sua aplicação com uma mensagem já preenchida com as respostas da calculadora. Só recebemos essa informação se carregar em Enviar. Quando nos contacta, usamos os dados que fornecer para responder, avaliar a obra e preparar uma proposta.",
        "Se aceitar a medição, registamos o clique num botão de WhatsApp, telefone ou email. Esse clique indica apenas que tentou abrir o canal; não confirma que uma mensagem foi enviada ou uma chamada atendida."]),
    ("Cookies e medição", [
        "O site usa armazenamento essencial para guardar a sua escolha de cookies. Com o seu consentimento, carrega a Google tag (Google Analytics e Google Ads) para medir visitas e campanhas. Pode aceitar ou manter apenas os essenciais, e mudar a escolha em «Gerir cookies», no rodapé. Recusar não impede o uso do site nem dos contactos.",
        "A escolha fica guardada neste navegador durante seis meses. Com consentimento, os parâmetros de campanha (UTM e identificadores de clique) são guardados durante a sessão para perceber a origem das visitas."]),
    ("Ligações externas", [
        f'A ligação «Deixe a sua avaliação no Google» abre o Google, que trata os dados segundo a sua própria política. A apresentação em PDF e a tabela de preços são ficheiros públicos e não recolhem dados.']),
    ("Finalidades e fundamento", [
        "Responder a pedidos e preparar propostas: diligências pré-contratuais a seu pedido. Executar obras e cumprir obrigações fiscais: execução de contrato e obrigação legal. Medição e publicidade: consentimento, que pode retirar a qualquer momento em «Gerir cookies»."]),
    ("Conservação", [
        "As respostas da calculadora não são guardadas pelo site. As mensagens recebidas são conservadas pelo tempo necessário ao pedido, à relação contratual e às obrigações legais (por exemplo, faturação)."]),
    ("Os seus direitos", [
        'Pode pedir acesso, retificação, apagamento, limitação, portabilidade ou oposição, quando aplicável, através de <a href="mailto:proimpermeabiliza@gmail.com">proimpermeabiliza@gmail.com</a>. Pode retirar o consentimento sem afetar o tratamento anterior. Tem direito a apresentar reclamação à <a href="https://www.cnpd.pt/" target="_blank" rel="noopener noreferrer">Comissão Nacional de Proteção de Dados</a>.']),
    ("Serviços utilizados", [
        'O site é publicado através do GitHub Pages, que regista dados técnicos de acesso (incluindo o endereço IP) para disponibilizar e proteger o serviço. Com consentimento, a Google tag carrega o Google Analytics e o Google Ads. Ao abrir o WhatsApp, o email ou o Google, passa a usar esses serviços. Consulte as políticas da <a href="https://docs.github.com/pt/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener noreferrer">GitHub</a>, da <a href="https://policies.google.com/privacy?hl=pt-PT" target="_blank" rel="noopener noreferrer">Google</a> e do <a href="https://www.whatsapp.com/legal/privacy-policy-eea" target="_blank" rel="noopener noreferrer">WhatsApp</a>, incluindo transferências internacionais.']),
]

LEGAIS = [
    ("Quem somos", [
        "ImpermeabilizaPro é o nome comercial de uma sociedade por quotas em constituição, com base em Sobral de Monte Agraço. A denominação, o NIF e a sede serão indicados aqui logo após o registo. Vinícius Nascimento é o responsável técnico.",
        'Contacto: <a href="tel:+351930446198">930 446 198</a> (chamada para a rede móvel nacional, telefone e WhatsApp) · <a href="mailto:proimpermeabiliza@gmail.com">proimpermeabiliza@gmail.com</a>.']),
    ("Preços, estimativas e propostas", [
        "Os preços do site e da calculadora são estimativas indicativas por m². Não são uma proposta nem um orçamento vinculativo. O valor, os trabalhos incluídos, o prazo, as condições de pagamento e os impostos aplicáveis são definidos na proposta escrita para cada obra, depois de vermos fotografias ou a obra.",
        f"Trabalhamos em coberturas, terraços e outras áreas planas a partir de {MIN} m². Não fazemos pequenas reparações, telhados de telha ou inclinados, nem trabalhos em grande altura.",
        "IVA: aplicamos a taxa legal (23%, ou 6% nas obras de habitação em que a lei o permite)."]),
    ("Fotografias e informação técnica", [
        "As fotografias mostram obras reais. A solução para cada obra depende da avaliação da superfície, dos remates e do sistema existente; as imagens e os textos não substituem essa avaliação."]),
    ("Reclamações e litígios de consumo", [
        'Para apresentar uma reclamação, contacte-nos pelos meios acima. Pode também usar o <a href="https://www.livroreclamacoes.pt/Inicio/" target="_blank" rel="noopener noreferrer">Livro de Reclamações Eletrónico</a>.',
        'Em caso de litígio de consumo, o consumidor pode recorrer a uma entidade de resolução alternativa de litígios de consumo. A lista das entidades está disponível no <a href="https://www.consumidor.gov.pt/" target="_blank" rel="noopener noreferrer">Portal do Consumidor</a>. O <a href="https://www.cniacc.pt/" target="_blank" rel="noopener noreferrer">CNIACC</a> (Centro Nacional de Informação e Arbitragem de Conflitos de Consumo) tem competência a nível nacional.']),
    ("Dados pessoais", [
        'Consulte a <a href="/privacidade/">Política de privacidade e cookies</a>.']),
]


def pagina_texto(slug, titulo, desc, h1, secoes, robots="noindex,follow", canonical=None, extra_head="", aviso=""):
    url = f"{SITE}/{slug}/"
    sec = "".join(f'<h2 id="{"cookies" if t.startswith("Cookies") else re.sub(r"[^a-z]+", "-", t.lower()).strip("-")}">{e(t)}</h2>' + "".join(f"<p>{p}</p>" for p in ps) for t, ps in secoes)
    corpo = (f'<section class="h-hero slim h-hero-texto"><div class="wrap"><p class="h-crumbs"><a href="/">Início</a> › {e(h1)}</p><h1>{e(h1)}</h1><p class="h-sub">{e(desc)}</p></div></section>'
             f'<section class="h-sec"><div class="wrap narrow h-artigo">{aviso}{sec}<p class="calc-legal">Atualizado em {HOJE}.</p></div></section>')
    head = cabeca(titulo, desc, canonical or url, [], robots=robots, extra_head=extra_head)
    return head + f"<main id=\"conteudo\">\n{corpo}\n</main>\n<footer></footer>\n</body>\n</html>\n"


def gerar_legais():
    paginas = {
        "privacidade": pagina_texto("privacidade", "Política de Privacidade e Cookies | ImpermeabilizaPro",
                                    "Como o site ImpermeabilizaPro trata informação quando usa a calculadora, navega ou nos contacta.", "Privacidade e cookies", PRIVACIDADE),
        "informacoes-legais": pagina_texto("informacoes-legais", "Informações Legais e Contactos | ImpermeabilizaPro",
                                           "Quem somos, como funcionam os preços e as propostas, reclamações e litígios de consumo.", "Informações legais e contactos", LEGAIS),
        "telhados": pagina_texto("telhados", "Telhados de Telha: Não Fazemos | ImpermeabilizaPro",
                                 "Não fazemos telhados de telha ou inclinados. Fazemos impermeabilização de coberturas planas, terraços e caves.", "Telhados de telha: não fazemos",
                                 [("O que fazemos", ['Impermeabilização de <a href="/coberturas-planas/">coberturas planas</a>, <a href="/terracos/">terraços</a> e <a href="/paredes/">caves e paredes enterradas</a>, a partir de ' + f"{MIN} m²."]),
                                  ("O que não fazemos", ["Telhados de telha ou inclinados, trabalhos em grande altura e pequenas reparações."])],
                                 canonical=f"{SITE}/coberturas-planas/", extra_head='<meta http-equiv="refresh" content="4;url=/coberturas-planas/">',
                                 aviso='<p class="h-resumo">Esta página antiga mudou. Vai ser encaminhado para <a href="/coberturas-planas/">coberturas planas</a> em poucos segundos.</p>'),
    }
    for slug, html_ in paginas.items():
        (RAIZ / slug).mkdir(exist_ok=True)
        (RAIZ / slug / "index.html").write_text(html_, encoding="utf-8")

if __name__ == "__main__":
    for slug, p in PAGINAS.items():
        d = RAIZ / slug
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(pagina(slug, p), encoding="utf-8")
    gerar_obras_guias()
    gerar_legais()
    apresentacao()
    tabela_home()
    sitemap()
    llms()
    print(f"{len(PAGINAS)} páginas geradas, sitemap e llms.txt atualizados.")
