# Plano de continuidade para Codex — ImpermeabilizaPro
Atualizado: 15-10-2026. **Este repositório é público**: este ficheiro contém apenas requisitos técnicos e comerciais não confidenciais. Não incluir credenciais, orçamentos privados, dados de clientes nem listas de prospeção.

## Objetivo
Website real, profissional, original, rápido e responsivo, mais útil do que versões genéricas, para captar **pedidos de orçamento reais** de impermeabilização através de SEO orgânico e confiança. Seguir o histórico em `WEBSITE_DECISIONS.md` e `MAPA_INFILT_ACAO_LEADS.md`; não inventar métricas, comentários ou projetos.

## Estado verificado no GitHub em 15-10-2026
- Repositório: `ImpermeabilizaPro/ImpermeabilizaPro`, branch `main`. Website estático GitHub Pages, `CNAME`, `sitemap.xml`, `index.html` e páginas de serviços/localidade.
- Existem `simulador/index.html`, `simulador/lead-delivery.js`, `lead-backend/worker.js`, `lead-backend/schema.sql`, `lead-backend/wrangler.jsonc`, `lead-backend/README.md`.
- **O backend de receção automática está preparado no código mas não foi comprovadamente ativado**. Atualmente o simulador prepara envio por WhatsApp/email; o visitante tem de efetuar o envio. Não apresentar um clique como pedido recebido.
- Alterações recentes incluem proposta de infraestrutura Cloudflare Worker + D1 + proteção anti-bot + email transacional; são **configurações ainda por realizar e testar**, não infraestrutura ativa.
- Esta verificação do GitHub **não comprova** o estado da publicação atual, o funcionamento do domínio, o relatório Search Console nem uma conversão real.

## Regras de serviço e comunicação
- (Atualizado a 13-11-2026) Apresentar como empresa: ImpermeabilizaPro é o nome comercial de uma sociedade por quotas em constituição. Não publicar denominação, NIF, alvará ou seguro antes de existirem.
- Serviços: terraços e coberturas planas, varandas, caves, garagens, paredes/infiltrações, casas de banho e sistemas de membrana/tela asfáltica/cimentícia conforme caso.
- **Não anunciar impermeabilização de telhados de telha/inclinados nem trabalhos de grande altura.** Auditar referências históricas a “telhados” no repositório e propor correções SEO/redirects sem quebrar URLs existentes; usar “coberturas planas” quando correto.
- Trabalho completo ou só mão de obra; pedidos de orçamento com dados suficientes e contacto simples por WhatsApp.
- Usar apenas fotografias verdadeiras, sem inventar avaliações, anos exatos, garantias, preços ou certificações.
- Conteúdo acessível e natural em português de Portugal.

## Trabalho para Codex desktop — executar em fases
**P0 Auditoria e checkpoint**
1. Ler `WEBSITE_DECISIONS.md`, `MAPA_INFILT_ACAO_LEADS.md` e `lead-backend/README.md`; `git status` e últimos commits. Verificar página inicial, simulador, serviços, conversão, SEO, links internos, sitemap e JavaScript.
2. Reproduzir e corrigir problemas **comprovados**, evitando alterações simultâneas gigantes. Testar áreas negativas, `null`/sem dados, contactos duplicados, rastreio sem consentimento e destino de redirects, especialmente URLs antigas com termo `telhados`.
**P1 Simulador honesto e útil**
3. Tornar o simulador de **estimativa indicativa**, nunca preço final garantido. Separar material/mão de obra quando adequado. Regras de preços devem ser calibradas com dados reais de obras/decisões do profissional; **não inventar tabelas de mercado**, nem colocar estimativas arbitrárias como oficiais.
4. Pedidos: manter fallback WhatsApp/email a funcionar sem backend. Só ativar envio automático depois de consentimento necessário, validação no servidor, segurança, armazenamento confirmado, monitorização de falhas, anti-spam, tratamento RGPD e testes de sucesso/erro/duplicados. Nunca simular sucesso.
**P2 Conteúdo, imagem e procura orgânica**
5. Melhorar hierarquia visual, mobile e performance; usar fotos autorizadas antes/durante/depois reais (apenas quando fornecidas), portfolio/cases factuais, chamadas claras, prova de confiança verdadeira. Facilitar pedido com poucas perguntas; compatibilidade mobile.
6. Rever SEO técnico: metadados, canonical, robots, sitemap, estruturas e ligações internas; analisar estados do Search Console antes de afirmar indexação. Preservar URLs já indexadas e só redirecionar com destino semanticamente adequado.
**P3 Publicação controlada**
7. Verificar automatização de testes, acessibilidade, consentimento de tracking, eventos medidos honestamente, navegação mobile, browsers e formulários. Validar publicação no domínio e não mudar tráfego, segredos, serviços pagos ou contas de anúncios sem instrução expressa.

## Critérios de aceitação
- Website não promete serviços que não são prestados, e identifica o profissional corretamente.
- Contactos nunca disparam falsos eventos 'lead recebido'.
- Simulador recusa entradas inválidas; não cria preços fictícios; fornece contexto e limitações da estimativa.
- Sem exposição de contactos de clientes, backups ou API keys. Nenhum email/teste é enviado a clientes reais.
- Desktop e smartphone com layout legível e formulários funcionais.
- SEO preserva páginas existentes e confirma publicação com URLs/regras efetivamente verificadas.

## Primeiro pedido a colar no Codex desktop
> Abre o repositório ImpermeabilizaPro/ImpermeabilizaPro. Lê CODEX_HANDOFF_2026-10-15.md e WEBSITE_DECISIONS.md. Faz P0 em primeiro lugar, sem inventar resultados nem alterar campanhas de anúncios. Corrige os erros comprovados em pequenos commits testados; prepara P1 para um simulador credível e pedidos reais, sem ativar backend até estar seguro e verificado. Preserva todo o trabalho atual e o site em produção.
