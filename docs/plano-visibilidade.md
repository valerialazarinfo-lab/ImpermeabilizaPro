# Plano de visibilidade gratuita: Google, Google Maps, Bing e IA

Atualizado: 2026-11-13. Objetivo: aparecer nos primeiros resultados sem anúncios pagos.
Não há forma honesta de garantir o 1.º lugar: depende da concorrência, das avaliações reais e do tempo. Este plano junta o que mais pesa, por ordem.

## O que já está feito no site (PR desta data)
- Página por serviço, por tipo de cliente (construtoras, condomínios) e por concelho (9 zonas), com conteúdo próprio, preços por m², fotografias reais e perguntas frequentes.
- Página de preços por m² em texto e tabela (`/precos-impermeabilizacao/`), que motores de pesquisa e IA conseguem ler e citar.
- Dados estruturados em todas as páginas: negócio (`HomeAndConstructionBusiness`), serviço com preço por m², perguntas frequentes e navegação.
- `llms.txt` na raiz: resumo factual para assistentes de IA (gerado a partir de `precos.csv`).
- `sitemap.xml` gerado automaticamente; páginas fracas ou fora do foco (`/simulador/`, `/telhados/`) com `noindex`.
- Site rápido no telemóvel (fotografia principal com 51 KB) e calculadora no topo de cada página para quem chega não sair.

## O que tens de fazer (por ordem de impacto)

### 1. Google Search Console (15 min) — sem isto o Google pode nem ver as páginas novas
1. Entrar em https://search.google.com/search-console com a conta que já tem acesso a `impermeabilizapro.pt`.
2. **Sitemaps** → enviar `https://impermeabilizapro.pt/sitemap.xml`.
3. **Inspeção de URL** → pedir indexação da página inicial, `/precos-impermeabilizacao/`, `/empresas/`, `/impermeabilizacao-condominios/` e das 4 zonas novas.
4. Voltar ao fim de 1 semana: ver **Páginas** (o que está indexado) e **Desempenho** (pesquisas que já trazem visitas).

### 2. Perfil da Empresa no Google (Google Maps) — guia em `docs/google-perfil-empresa.md`
- Completar tudo: categoria, serviços, área de serviço, descrição, fotografias reais, horário.
- Website: `https://impermeabilizapro.pt/?utm_source=google&utm_medium=organic&utm_campaign=gbp`.
- Publicar 1 fotografia de obra por semana.
- **Avaliações** são o fator n.º 1 no Maps: pedir a todos os clientes no fim da obra (mensagens prontas no guia). Nunca oferecer nada em troca.

### 3. Bing Webmaster Tools e Bing Places (30 min) — é o que o ChatGPT usa para pesquisas locais
1. https://www.bing.com/webmasters → **Importar do Google Search Console** (mais rápido) → enviar o sitemap.
2. https://www.bingplaces.com → **importar do Perfil da Empresa no Google** depois de este estar completo.
- Fontes: o ChatGPT faz uma pesquisa no Bing e usa os 20–30 primeiros resultados ([Search Engine Land](https://searchengineland.com/how-does-chatgpt-conduct-local-searches-454894)); 58% das fontes que cita são sites das próprias empresas ([BrightLocal](https://brightlocal.com/research/uncovering-chatgpt-search-sources/)).

### 4. Apple Business Connect (15 min) — Mapas do iPhone e Siri
- https://businessconnect.apple.com → mesmo nome, telefone, site e área que no Google.

### 5. Diretórios e perfis gratuitos (1 a 2 horas, uma vez)
Usar **sempre** o mesmo nome, telefone e site: `ImpermeabilizaPro · 930 446 198 · https://impermeabilizapro.pt`.
- Facebook (página de negócio) e Instagram: fotografias das obras.
- LinkedIn (página): importante para construtoras.
- Diretórios portugueses citados em guias de SEO local: Cylex Portugal, Empresas.pt, Zipleo ([Ranktracker](https://www.ranktracker.com/blog/a-complete-guide-for-doing-local-seo-in-portugal)). Verificar que o registo é gratuito antes de submeter; ignorar ofertas pagas de «citações».
- Habitissimo e Fixando: perfil gratuito com fotografias (os pedidos podem ser pagos; decidir depois).
- Fornecedores: perguntar à Imperalum e ao distribuidor de material se têm lista de aplicadores no site.

### 6. Pedir ligações (o que mais faz subir no Google)
- Construtoras e administrações de condomínio com quem trabalharem: pedir para incluir a ImpermeabilizaPro como parceiro/fornecedor no site delas.
- Associações locais e câmaras (diretórios de empresas do concelho de Sobral de Monte Agraço, Arruda, Alenquer).

### 7. Rotina mensal (30 min)
- Search Console: que pesquisas dão cliques → criar ou melhorar a página dessa pesquisa.
- Acrescentar 1 obra nova com fotografias (m², sistema, localidade) ao site e ao perfil Google.
- Atualizar `calculadora/precos.csv` se os preços mudarem e correr `python3 scripts/gerar_paginas.py`.

## Quando a garantia, alvará, seguro e avaliações existirem
Enviar os dados para os pôr no site e nos dados estruturados: são o que mais falta face aos concorrentes (ver `docs/concorrentes.md`).
