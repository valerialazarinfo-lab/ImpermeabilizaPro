# Calculadora e páginas geradas

- Página: `/calculadora/` e bloco no topo de cada página (`calculadora/widget.mjs`, estilos em `calculadora/calc.css`).
- Motor: `calculadora/motor.mjs` (testes: `node --test calculadora/motor.test.mjs`).
- Preços: `calculadora/precos.csv` — fonte única, com a origem de cada valor. Abre no Excel (separador `;`).

## Mudar preços
1. Editar `min`/`max` no CSV (valores **sem IVA**, antes do fator de entrada) e a coluna `origem`.
2. Nível de preço: `config;fator_preco_entrada` (1 = preço médio de mercado, decisão de 13-11-2026; o mínimo do intervalo dá ≥50% de margem sobre os custos conhecidos do Lumiar. Não baixar sem refazer as contas de margem).
3. Correr: `python3 scripts/gerar_paginas.py && python3 scripts/harmonizar_layout.py && python3 scripts/verificar_site.py`
   (atualiza tabelas das páginas, `llms.txt` e sitemap).
4. Mudar o `?v=` de `precos.csv` em `calculadora/widget.mjs` para limpar a cache.

## Mínimo de obra
`python3 scripts/definir_minimo_obra.py 200` e depois os comandos do passo 3.

## Como o intervalo é calculado
Mínimo = melhor caso −5%; máximo = pior caso +5%. Nas respostas «Não sei», o melhor caso usa o mínimo da linha e o pior caso o máximo (o máximo mostrado cobre sempre o pior caso das respostas desconhecidas). As tabelas das páginas usam a mesma regra (valor médio ± 5%). Desconto por área (grupo `escala`).
IVA: 23% para todos enquanto `config;autoliquidacao_ativa` = 0. Com alvará/certificado IMPIC válido, pôr 1: empresas passam a ver preço com autoliquidação (DL 97/2026).

## Conteúdo das páginas
Textos, fotografias e perguntas de cada página de serviço, preço e zona estão em `scripts/gerar_paginas.py` (PAGINAS, LOCAIS).
Cabeçalho e rodapé: `scripts/partials/`. Página inicial: `index.html` (a tabela de preços é inserida pelo gerador).
