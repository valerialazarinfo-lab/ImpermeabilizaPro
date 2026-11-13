# Fase 1 — ligações, SEO e medição

Data: 15 de outubro de 2026  
Base: `main` em `6c6ecc4`  
Branch de revisão: `codex/fase-1-seo-links-medicao`

## Alterações preparadas

1. Nas páginas `privacidade/index.html` e `informacoes-legais/index.html`, quatro ligações internas com o texto «Coberturas planas» passaram de `/telhados/` para `/coberturas-planas/`.
2. Em `script.js`, a query histórica `/?servico=telhados` passa a encaminhar diretamente para `/coberturas-planas/`. O código continua a preservar os outros parâmetros e o fragmento da URL. Os destinos de `terracos` e `paredes` mantêm-se.
3. Em `index.html`, a versão da URL de `script.js` foi atualizada para evitar que a página inicial continue a carregar uma cópia em cache do encaminhamento anterior.
4. Em `privacidade/index.html`, a referência desatualizada à Netlify foi substituída por GitHub Pages, com ligação à política de privacidade da GitHub e data de atualização. Não foram alterados os restantes termos legais.
5. Em `script.js`, comentários que pressupunham um estatuto de conversão na conta Google Ads passaram a indicar que essa configuração precisa de verificação externa. Não foram alterados nomes, destinos ou condições de emissão de eventos.

## Redirecionamento HTTP 301

A regra `/telhados/ /coberturas-planas/ 301!` está em `_redirects`, formato documentado pela Netlify. Em 15-10-2026, um pedido `HEAD` a `https://impermeabilizapro.pt/telhados/` devolveu **200**, sem cabeçalho `Location`; a produção é servida pelo GitHub Pages. A regra não está a produzir o 301 pretendido.

`telhados/index.html` foi preservado: continua com `noindex,follow`, canónica para `/coberturas-planas/` e atualização por meta tag. O sitemap continua a incluir `/coberturas-planas/` e a omitir `/telhados/`. Esta situação evita apagar uma URL antiga antes de existir uma solução de encaminhamento HTTP testada. Um 301 requer uma capacidade de redirecionamento no alojamento ou na camada de distribuição, que não foi configurada nesta fase. A configuração de domínio/DNS e os dados de indexação do Search Console devem ser consultados antes de uma decisão.

Documentação: [GitHub Pages é alojamento estático](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages); [sintaxe de `_redirects` da Netlify](https://docs.netlify.com/manage/routing/redirects/overview/).

## Auditoria dos eventos de contacto

| Evento emitido pelo website | Significado comprovado no código | Não comprova |
| --- | --- | --- |
| `ip_whatsapp_click` | Tentativa de abrir WhatsApp; uma ocorrência por sessão após consentimento. | Mensagem enviada ou recebida. |
| `ip_phone_click` | Clique num link `tel:`; uma ocorrência por sessão após consentimento. | Chamada estabelecida ou qualificada. |
| `ip_email_click` | Clique num link `mailto:`; uma ocorrência por sessão após consentimento. | Email enviado ou recebido. |
| `ip_whatsapp_request_prepared` | Mensagem gerada pelo pedido rápido após validação dos campos. | Pedido recebido. |

O script envia os eventos para a propriedade GA4 `G-BBSN5Z50XK` com `send_to`, depois de consentimento aceite. Configura também o destino Google Ads `AW-18418470072` e a configuração de chamadas do website após consentimento. O contentor GTM histórico não é carregado pelo código atual. O simulador prepara WhatsApp/email manualmente e não comprova receção.

Existe uma divergência histórica: `WEBSITE_DECISIONS.md` regista uma renomeação em 25-09-2026 para eventos terminados em `_observed`, mas `script.js` emite os nomes antigos. Não há nesta revisão acesso verificado à configuração atual de eventos chave no GA4, importações, ações primárias/secundárias ou regras de conversão na conta Ads. **Nenhum nome de evento ou configuração de conversão foi alterado.** O próximo passo é obter um inventário atual dessas configurações e testar a cadeia de medição antes de qualquer mudança.

## Testes efetuados

- `node --check script.js`: passou.
- Execução isolada da lógica de encaminhamento em Node: cinco cenários passaram, incluindo `telhados` com UTM, `gclid` e fragmento; `terracos`; `paredes`; serviço desconhecido; e query numa página diferente da inicial.
- Análise estática de 21 páginas HTML: 572 referências locais `href`/`src` e fragmentos internos verificados sem destino inexistente. JSON-LD analisável como JSON; sitemap XML analisável.
- Comparação com a base Git: canónicas e dados estruturados das páginas alteradas preservados; `sitemap.xml`, `robots.txt`, `/telhados/` e `/coberturas-planas/` sem alterações.
- Pré-visualização local em navegador: páginas de privacidade, informações legais e coberturas planas verificadas a 390, 768 e 1280 px. Sem transbordamento horizontal nessas larguras; ambas as ligações «Coberturas planas» das páginas legais apontam para `/coberturas-planas/`. A query histórica navegou para `/coberturas-planas/?utm_source=teste#pedido`.
- Produção, apenas leitura: `HEAD` devolveu 200 para `/`, `/coberturas-planas/`, `/telhados/`, `/privacidade/` e `/informacoes-legais/`. Isto verifica o estado anterior à publicação da branch, não o resultado das alterações propostas.
- `git diff --check`: passou.

Não foram enviados pedidos reais, mensagens, emails ou chamadas. Não foram executados testes de entrega de eventos GA4/Ads nem testes em dispositivos físicos/Safari.

## Pendente antes de publicação

1. Rever esta branch e confirmar o método de publicação. Nenhuma alteração foi enviada para a branch de produção.
2. Consultar Search Console e o fornecedor de DNS/distribuição para decidir e testar o 301 de `/telhados/`, mantendo a URL antiga até haver substituição segura.
3. Consultar as configurações reais de GA4 e Ads, sobretudo eventos chave, importações e ações primárias/secundárias associadas aos nomes antigos e `_observed`. Não tratar cliques como leads recebidos.
4. Depois de publicar, repetir testes de rotas e navegação no domínio real e confirmar que a página inicial serve a versão nova de `script.js`.
5. Avaliar separadamente a adequação do GitHub Pages ao uso comercial, à luz das [condições oficiais](https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features). Esta revisão não altera o alojamento.
