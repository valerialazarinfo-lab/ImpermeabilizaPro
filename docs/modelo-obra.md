# Modelo de página de obra

Cada obra terminada pode dar uma página em `/obras/<slug>/`. O modelo está em `scripts/gerar_paginas.py` (`MODELO_OBRA`).
Fotografias na lista de `docs/fotos-obra-checklist.md`. Este repositório é público: aqui só entra o que vai aparecer no site.

## Dados a recolher (só factos reais)
| Campo | Exemplo | Obrigatório |
|---|---|---|
| Localidade (concelho, nunca a morada) | Torres Vedras | sim |
| Área | 320 m² | sim |
| Tipo | Terraço sobre garagem / cobertura plana / cave | sim |
| Sistema e marca | Duas camadas de tela asfáltica, marca X | sim |
| Acabamento | Mineral em xisto | se houver |
| Tipo de cliente (nunca o nome sem autorização) | Construtora / condomínio / empresa | não |
| Data (mês e ano) | outubro de 2026 | não |
| Duração | 6 dias | não |
| O problema ou pedido | Infiltrações na garagem por baixo do terraço | sim |
| A solução e o ponto mais difícil | Remates nas platibandas e nos ralos | sim |
| Fotografias antes, durante e depois | ver lista de fotografias | pelo menos 3 |
| **Autorização escrita do cliente para publicar** | email ou mensagem guardada no Drive | **sim** |

## Como publicar
1. Copiar `MODELO_OBRA` para dentro de `OBRAS`, com slug `localidade-tipo-areaM2` (ex.: `torres-vedras-terraco-320m2`).
2. Substituir todos os `[...]` por dados reais. O gerador recusa publicar se ficar algum.
3. Pôr as fotografias em `assets/` (WebP, sem aumentar a resolução), juntar as chaves em `F` e usar essas chaves em `fases`.
4. Imagem principal: `caso-<slug-curto>.webp` (1200×675) e `caso-<slug-curto>-600.webp` (600 px).
5. Só com a autorização guardada: `publicar=True` e `autorizacao_cliente=True`. Sem isto o gerador para com erro.
6. Correr o fluxo da skill (`gerar_paginas.py`, `harmonizar_layout.py`, `gerar_pdf.js`, `verificar_site.py`).

Enquanto `publicar=False`, a obra não aparece em lado nenhum: nem página, nem sitemap, nem índice de obras, nem `llms.txt`, nem PDF.
