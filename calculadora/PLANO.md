# Calculadora e páginas geradas

- Página: `/calculadora/` e bloco no topo de cada página (`calculadora/widget.mjs`, estilos em `calculadora/calc.css`).
- Motor: `calculadora/motor.mjs` (testes: `node --test calculadora/motor.test.mjs`).
- Preços: `calculadora/precos.csv` — fonte única, com a origem de cada valor. Abre no Excel (separador `;`).

## Mudar preços
1. Editar `min`/`max` no CSV (valores **sem IVA**, antes do fator de entrada) e a coluna `origem`.
2. Preço de entrada: `config;fator_preco_entrada` (0,9 = 10% abaixo do mercado; 1 = preço de mercado).
3. Correr: `python3 scripts/gerar_paginas.py && python3 scripts/harmonizar_layout.py && python3 scripts/verificar_site.py`
   (atualiza tabelas das páginas, `llms.txt` e sitemap).
4. Mudar o `?v=` de `precos.csv` em `calculadora/widget.mjs` para limpar a cache.

## Mínimo de obra
`python3 scripts/definir_minimo_obra.py 200` e depois os comandos do passo 3.

## Como o intervalo é calculado
Valor médio de cada resposta ± 5%; cada «Não sei» acrescenta 3% (máximo ±12%). As tabelas das páginas usam a mesma regra (valor médio ± 5%). Desconto por área (grupo `escala`).
IVA: 23% para todos enquanto `config;autoliquidacao_ativa` = 0. Com alvará/certificado IMPIC válido, pôr 1: empresas passam a ver preço com autoliquidação (DL 97/2026).

## Conteúdo das páginas
Textos, fotografias e perguntas de cada página de serviço, preço e zona estão em `scripts/gerar_paginas.py` (PAGINAS, LOCAIS).
Cabeçalho e rodapé: `scripts/partials/`. Página inicial: `index.html` (a tabela de preços é inserida pelo gerador).
