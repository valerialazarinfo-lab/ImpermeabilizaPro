---
name: site-impermeabilizapro
description: Melhorar, gerar, testar e publicar o site impermeabilizapro.pt (calculadora, preços, páginas de serviço/zona/obras/guias, SEO, páginas legais). Usar sempre que o pedido for sobre o site da ImpermeabilizaPro.
---

# Site impermeabilizapro.pt: como trabalhar

Fala com a Valeria em português de Portugal. Esta skill é só para o site. Custos internos, margens e CRM tratam-se noutra conversa, com o Google Drive como base de dados: daqui não se mexe nisso.

## Regras que não se quebram
- Ler primeiro `AGENTS.md` e `WEBSITE_DECISIONS.md` (decisões com data).
- Repositório **público**: nunca pôr custos internos, dados de clientes, orçamentos, segredos ou IDs do Drive.
- Nunca inventar avaliações, obras, garantias, alvará, seguro, certificações nem números. Fotografias só reais.
- Público: construtoras, condomínios e empresas; obras a partir do mínimo (hoje 100 m²) em coberturas e áreas planas. Não anunciar telhados de telha/inclinados, grande altura nem pequenas reparações. Casas de banho = serviço à parte, sem preço automático.
- Empresa: «ImpermeabilizaPro, sociedade por quotas em constituição». Denominação, NIF, sede, alvará e seguro só depois de existirem.
- IVA à taxa legal (23%; 6% quando a lei permite). Autoliquidação desligada (`config;autoliquidacao_ativa` = 0) até haver alvará/certificado IMPIC (DL 97/2026).
- WhatsApp/email abrem mensagens preenchidas; nunca dizer «pedido recebido». Medição só com consentimento e só categorias.
- Nunca fazer merge em `main` sem a Valeria dizer «podes publicar» para essa alteração.

## Onde está cada coisa (fonte única)
| O quê | Ficheiro |
|---|---|
| Preços, mínimo, IVA, margem do intervalo, escala, «só mão de obra» | `calculadora/precos.csv` (coluna `origem` obrigatória; linhas «HIPÓTESE» não vão para tabelas públicas) |
| Motor da calculadora e testes | `calculadora/motor.mjs`, `calculadora/motor.test.mjs` |
| Calculadora no ecrã | `calculadora/widget.mjs`, `calculadora/calc.css` |
| Conteúdo das páginas de serviço, preço, zona, obras, guias, legais, `/telhados/`, PDF, sitemap, `llms.txt` | `scripts/gerar_paginas.py` (PAGINAS, LOCAIS, OBRAS, GUIAS, PRIVACIDADE, LEGAIS) |
| Cabeçalho, rodapé, cookies, botão móvel | `scripts/partials/` + `scripts/harmonizar_layout.py` |
| Página inicial | `index.html` (a tabela de preços é inserida pelo gerador) |
| Estilos | `assets/b2b.css`, `calculadora/calc.css`, `style.css` (limpo; não acrescentar regras antigas) |
| Mínimo de obra | `python3 scripts/definir_minimo_obra.py <m²>` |
| Ícones (favicon, Apple) e imagens de partilha 1200×630 | `python3 scripts/gerar_imagens.py` (fotos reais; nova chave em `F` do gerador = acrescentar em `OG`) |
| Página de erro | `404.html`, gerada por `pagina_404()` no gerador |

## Fluxo de cada alteração
1. `git fetch origin main` e criar ramo novo `claude/<tema>` a partir de `origin/main` (outras conversas também publicam: partir sempre do `main` atual).
2. Editar a **fonte** (nunca o HTML gerado à mão, exceto `index.html` e `calculadora/index.html`).
3. Gerar e verificar:
   ```
   python3 scripts/gerar_paginas.py
   python3 scripts/harmonizar_layout.py
   node scripts/gerar_pdf.js
   python3 scripts/verificar_site.py
   node --test calculadora/motor.test.mjs
   ```
4. Mudar o `?v=` dos ficheiros CSS/JS alterados (cache dos visitantes).
5. Testar no navegador (Playwright, 390 px e 1366 px): sem erros JS, sem deslocamento horizontal, calculadora com preço, abaixo do mínimo e com «Não sei». Para mudanças de layout ou desempenho, correr o Lighthouse (telemóvel) e não aceitar descidas.
6. Commits pequenos em português; PR com resumo, testes e o que falta confirmar.
7. Mostrar à Valeria o que muda (números e capturas quando houver mudança visual) e perguntar se pode publicar.
8. Com «podes publicar»: esperar a verificação «verificar» do PR passar, fazer merge, esperar «pages build and deployment» com sucesso e confirmar o deploy. Dizer o que verificar no site real (Ctrl+F5).

## Preços (resumo das decisões de 13-11-2026)
- Nível: preço médio de mercado (`fator_preco_entrada` = 1). Não baixar sem refazer as contas de margem na conversa de custos.
- Intervalo ±5%; nas respostas «Não sei», mínimo = melhor caso e máximo = pior caso. Material recomendado pré-escolhido por superfície.
- Quando a Valeria colar uma tabela nova vinda da conversa de custos (formato do CSV), substituir as linhas, correr o fluxo acima e mostrar antes/depois.

## Pendentes que dependem da Valeria
Custos reais (remoção, remates, ralos, só mão de obra), registo da Lda (denominação, NIF, sede), alvará IMPIC, seguro, garantia, avaliações Google, fotografias de obras novas (`docs/fotos-obra-checklist.md`), conta Cloudflare (formulário e 301 de `/telhados/`), factos para «Sobre nós».
