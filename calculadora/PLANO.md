# Calculadora de estimativas

Página pública: `/calculadora/` (`index.html`). Motor: `motor.mjs`. Preços: `precos.csv` (fonte única, com a origem de cada valor).

## Como editar preços
1. Abrir `precos.csv` no Excel/Google Sheets (separador `;`) ou num editor de texto.
2. Alterar `min`/`max` e atualizar a coluna `origem` (ex.: «Obra X, nov. 2026»). Valores **sem IVA**.
3. Correr `node --test calculadora/motor.test.mjs`.
4. Mudar o `?v=` de `precos.csv` em `index.html` para os visitantes não verem a versão antiga em cache.

## Mínimo de obra
`python3 scripts/definir_minimo_obra.py 200` muda o mínimo em todo o site (CSV + todas as páginas). `--verificar` confirma que está alinhado.

## Regras
- Abaixo do mínimo: aviso, sem preço.
- Telhados inclinados/de telha e grande altura: excluídos (AGENTS.md).
- Andaime, fora da zona, área enorme ou demasiados ralos: avaliação sem preço.
- IVA à taxa normal (23%) por defeito; nota sobre a taxa reduzida.
- O WhatsApp abre com a mensagem; nunca se diz que o pedido foi recebido.

## Antes de dar como definitivo
Valores marcados «HIPÓTESE» no CSV têm de ser confirmados pelo Vinícius com 3 obras reais (custos, margem, deslocação).
