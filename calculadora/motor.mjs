/*
 * Motor da calculadora ImpermeabilizaPro. Não contém preços: tudo vem de precos.csv (fonte única).
 * Funciona no navegador (import) e em Node (testes: node --test calculadora/motor.test.mjs).
 *
 * Cálculo (valor médio de cada linha = (min + max) / 2):
 *   €/m²   = material × fator da superfície + soma das respostas em €/m²
 *   total  = (€/m² × área × fator de escala + ralos × €/ralo) × produto de (1 + %) × fator de preço de entrada
 *   intervalo = total × (1 ± margem); margem = base + extra por cada «Não sei» (até ao máximo)
 *   IVA: taxa legal; autoliquidação para empresas só com config autoliquidacao_ativa = 1 (exige alvará/certificado IMPIC).
 */

export const PERGUNTAS = ['cliente', 'superficie', 'material', 'suporte', 'remocao', 'acesso', 'remates', 'isolamento', 'acabamento', 'urgencia', 'localizacao'];
const EXTRAS = ['suporte', 'remocao', 'acesso', 'remates', 'isolamento', 'acabamento', 'urgencia', 'localizacao'];

/** Lê o CSV (separador «;», decimal com vírgula ou ponto, linhas começadas por «#» ignoradas). */
export function lerPrecos(texto) {
  const linhas = String(texto).replace(/^﻿/, '').split(/\r?\n/);
  let cab = null;
  const t = {};
  for (const bruta of linhas) {
    const linha = bruta.trim();
    if (!linha || linha.startsWith('#')) continue;
    let cols = linha.split(';').map((c) => c.trim());
    if (!cab) { cab = cols; continue; }
    if (cols.length > cab.length) cols = [...cols.slice(0, cab.length - 1), cols.slice(cab.length - 1).join('; ')];
    const r = Object.fromEntries(cab.map((h, i) => [h, cols[i] ?? '']));
    if (!r.grupo || !r.chave) throw new Error('Linha sem grupo/chave: ' + linha);
    const num = (v) => Number(String(v).replace(',', '.'));
    const item = { grupo: r.grupo, chave: r.chave, descricao: r.descricao, min: num(r.min), max: num(r.max), unidade: r.unidade, regras: r.regra.split(',').map((s) => s.trim()).filter(Boolean), origem: r.origem };
    if (r.min === '' || r.max === '' || !Number.isFinite(item.min) || !Number.isFinite(item.max) || item.max < item.min) {
      throw new Error(`Valores inválidos em ${r.grupo}/${r.chave}`);
    }
    (t[r.grupo] ||= {})[r.chave] = item;
  }
  for (const k of ['minimo_obra_m2', 'autoliquidacao_ativa', 'fator_preco_entrada', 'iva_percentagem', 'area_maxima_m2', 'ralos_maximo', 'margem_base_percentagem', 'margem_nao_sei_percentagem', 'margem_maxima_percentagem']) {
    if (!t.config?.[k]) throw new Error('Falta config;' + k + ' em precos.csv');
  }
  if (!t.extra?.ralo) throw new Error('Falta extra;ralo em precos.csv');
  if (!t.escala) throw new Error('Falta o grupo escala em precos.csv');
  for (const g of PERGUNTAS) if (!t[g]) throw new Error('Falta o grupo ' + g + ' em precos.csv');
  return t;
}

export const minimoObra = (t) => t.config.minimo_obra_m2.min;
export const autoliquidacaoAtiva = (t) => t.config.autoliquidacao_ativa.min === 1;
const med = (i) => (i.min + i.max) / 2;
const arred = (v, passo) => Math.round(v / passo) * passo;
const cfg = (t, k) => t.config[k].min;

export function fatorEscala(area, t) {
  let melhor = null;
  for (const e of Object.values(t.escala)) if (area >= Number(e.chave) && (!melhor || Number(e.chave) > Number(melhor.chave))) melhor = e;
  return melhor ? med(melhor) : 1;
}

/** estado: 'preco' | 'abaixo_minimo' | 'avaliacao' | 'excluido' | 'invalido' */
export function calcular(entrada, t) {
  const area = Number(String(entrada.area ?? '').replace(',', '.'));
  const minimo = minimoObra(t);
  const sup = t.superficie[entrada.superficie];
  if (sup?.regras.includes('servico_a_parte')) {
    return { estado: 'avaliacao', motivo: 'As casas de banho e zonas interiores são um serviço à parte: o orçamento é feito depois de vermos fotografias. O mínimo de m² não se aplica.' };
  }
  if (sup?.regras.includes('excluido')) return { estado: 'excluido', motivo: `${sup.descricao}: este trabalho não é feito pela ImpermeabilizaPro.` };
  if (!Number.isFinite(area) || area <= 0) return { estado: 'invalido', falta: 'area', motivo: 'Indique a área aproximada em m².' };
  if (area < minimo) return { estado: 'abaixo_minimo', minimo, motivo: `O mínimo de obra é ${minimo} m².` };
  if (area > cfg(t, 'area_maxima_m2')) {
    return { estado: 'avaliacao', motivo: `Para áreas acima de ${cfg(t, 'area_maxima_m2').toLocaleString('pt-PT')} m² preparamos sempre uma proposta à medida.` };
  }

  const esc = {};
  for (const g of PERGUNTAS) {
    esc[g] = t[g][entrada[g]];
    if (!esc[g]) return { estado: 'invalido', falta: g, motivo: 'Responda a todas as perguntas.' };
  }
  for (const g of PERGUNTAS) {
    if (esc[g].regras.includes('excluido')) return { estado: 'excluido', motivo: `${esc[g].descricao}: este trabalho não é feito pela ImpermeabilizaPro.` };
  }
  for (const g of PERGUNTAS) {
    if (esc[g].regras.includes('avaliacao')) return { estado: 'avaliacao', motivo: `${esc[g].descricao}: precisamos de ver fotografias antes de indicar um valor.` };
  }
  const ralosTxt = String(entrada.ralos ?? '').trim();
  const ralos = ralosTxt === '' ? 0 : Number(ralosTxt);
  if (!Number.isInteger(ralos) || ralos < 0) return { estado: 'invalido', falta: 'ralos', motivo: 'Indique o número de ralos (0 se não houver).' };
  if (ralos > cfg(t, 'ralos_maximo')) return { estado: 'avaliacao', motivo: 'Muitos ralos ou pontos de escoamento: precisamos de ver a obra.' };

  const aceites = esc.superficie.regras.filter((r) => r.startsWith('materiais:')).flatMap((r) => r.slice(10).split('|'));
  let matMed;
  if (esc.material.chave === 'nao_sei') {
    const op = aceites.map((k) => t.material[k]).filter(Boolean);
    if (!op.length) return { estado: 'avaliacao', motivo: 'Precisamos de ver a obra para indicar a solução.' };
    matMed = (Math.min(...op.map((o) => o.min)) + Math.max(...op.map((o) => o.max))) / 2;
  } else if (aceites.length && !aceites.includes(esc.material.chave)) {
    return { estado: 'invalido', falta: 'material', motivo: `${esc.material.descricao} não é a solução que usamos em ${esc.superficie.descricao.toLowerCase()}. Escolha outro material ou «Não sei».` };
  } else {
    matMed = med(esc.material);
  }

  const extras = EXTRAS.map((g) => esc[g]);
  const porM2 = matMed * med(esc.superficie) + extras.filter((i) => i.unidade === '€/m²').reduce((s, i) => s + med(i), 0);
  const fator = extras.filter((i) => i.unidade === '%').reduce((f, i) => f * (1 + med(i) / 100), 1);
  const escala = fatorEscala(area, t);
  const semIva = (porM2 * area * escala + ralos * med(t.extra.ralo)) * fator * cfg(t, 'fator_preco_entrada');

  const naoSei = PERGUNTAS.filter((g) => esc[g].regras.includes('nao_sei')).length;
  const margem = Math.min(cfg(t, 'margem_maxima_percentagem'), cfg(t, 'margem_base_percentagem') + naoSei * cfg(t, 'margem_nao_sei_percentagem')) / 100;
  const autoliquidacao = esc.cliente.regras.includes('autoliquidacao') && cfg(t, 'autoliquidacao_ativa') === 1;
  const iva = autoliquidacao ? 0 : cfg(t, 'iva_percentagem');
  const m2 = (v) => ({ min: Math.round((v * (1 - margem)) / area), max: Math.round((v * (1 + margem)) / area) });
  const tot = (v) => ({ min: arred(v * (1 - margem), 50), max: arred(v * (1 + margem), 50) });
  return {
    estado: 'preco',
    area,
    ralos,
    iva,
    autoliquidacao,
    margem: Math.round(margem * 100),
    naoSei,
    escala,
    m2SemIva: m2(semIva),
    m2ComIva: m2(semIva * (1 + iva / 100)),
    totalSemIva: tot(semIva),
    totalComIva: tot(semIva * (1 + iva / 100)),
    notas: PERGUNTAS.map((g) => esc[g]).filter((i) => i.regras.includes('nota')).map(notaDe),
  };
}

function notaDe(i) {
  if (i.chave === 'nao_sei') return `${i.grupo === 'suporte' ? 'Estado do suporte' : 'Remoção do sistema antigo'} por confirmar: com fotografias o intervalo fica mais estreito.`;
  if (i.chave === 'ceramico_novo') return 'O pavimento cerâmico novo não está incluído: é orçamentado à parte.';
  if (i.chave === 'levantar_ceramico') return 'Inclui levantar o pavimento existente, não a colocação de pavimento novo.';
  if (i.chave === 'urgente') return 'Com água a entrar, pode ser preciso localizar a origem antes de impermeabilizar.';
  return i.descricao;
}
