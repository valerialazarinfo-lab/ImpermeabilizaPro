# Calculadora de estimativas V1

Estado: preparação interna. Não publicar estimativas sem validação técnica e fiscal.

## Entrada
Serviço, área aproximada em m², localidade, estado da base, preparação, remates, acessos, fotos opcionais, urgência e contacto com consentimento RGPD separado do marketing.

## Regras
- Intervalo base: área × preços mínimo/máximo por m² da configuração provisória.
- Não duplicar preparação se já estiver incluída no serviço selecionado.
- Considerar custo mínimo comercial de obra completa como critério de triagem; nunca forçar preços sem análise.
- Acessos difíceis, infiltração sem diagnóstico, área desconhecida ou trabalhos excluídos: avaliação manual sem preço automático.
- Valores base sem IVA; antes de exibir total final, confirmar tratamento fiscal aplicável. Não apresentar preços sem IVA como preço final a particulares.
- Não confundir estimativa automática com orçamento vinculativo.

## Backend a verificar antes de implementar
Verificar se Cloudflare Worker, D1, Turnstile, Resend e notificações já existem. Nunca publicar chaves ou preços internos confidenciais no frontend. Aplicar validação server-side, limitação de pedidos, consentimento, retenção de dados e testes ponta a ponta.

## Testes obrigatórios
Áreas 8, 40 e 100 m²; inputs inválidos; área desconhecida; preparação moderada; remates complexos; exclusões; IVA; envio duplicado; falha do email; dispositivos móveis; eventos analíticos com consentimento.

## Aprovação
Validar 3 casos reais com Vinícius, custos e margens antes de disponibilizar ao público. Não alterar main, DNS ou produção nesta fase.
