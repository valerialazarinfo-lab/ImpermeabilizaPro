/*
 * Motor da calculadora de estimativas ImpermeabilizaPro.
 * Não contém preços: todos os valores vêm de precos.csv (fonte única).
 * Funciona no navegador (import) e em Node (testes: node --test calculadora/).
 *
 * Para o mínimo e para o máximo do intervalo:
 *   €/m² sem IVA = material × fator da superfície + soma das respostas em €/m²
 *   subtotal     = €/m² × área + ralos × €/ralo
 *   total s/ IVA = subtotal × produto de (1 + %) das respostas em %
 *   total c/ IVA = total s/ IVA × (1 + IVA)
 */

export const PERGUNTAS = ['superficie', 'material', 'suporte', 'remocao', 'acesso', 'remates', 'isolamento', 'acabamento', 'urgencia', 'localizacao'];

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
    // Um «;» dentro da última coluna (origem) não parte a linha.
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
  for (const k of ['minimo_obra_m2', 'iva_percentagem', 'area_maxima_m2', 'ralos_maximo']) {
    if (!t.config?.[k]) throw new Error('Falta config;' + k + ' em precos.csv');
  }
  if (!t.extra?.ralo) throw new Error('Falta extra;ralo em precos.csv');
  for (const g of PERGUNTAS) if (!t[g]) throw new Error('Falta o grupo ' + g + ' em precos.csv');
  return t;
}

export const minimoObra = (t) => t.config.minimo_obra_m2.min;
const arred = (v, passo) => Math.round(v / passo) * passo;

/**
 * estado: 'preco' | 'abaixo_minimo' | 'avaliacao' | 'excluido' | 'invalido'
 */
export function calcular(entrada, t) {
  const area = Number(String(entrada.area ?? '').replace(',', '.'));
  const minimo = minimoObra(t);
  const sup = t.superficie[entrada.superficie];
  if (sup?.regras.includes('excluido')) return { estado: 'excluido', motivo: `${sup.descricao}: este trabalho não é feito pela ImpermeabilizaPro.` };
  if (!Number.isFinite(area) || area <= 0) return { estado: 'invalido', motivo: 'Indique a área aproximada em m².' };
  if (area < minimo) return { estado: 'abaixo_minimo', minimo, motivo: `O mínimo de obra é ${minimo} m².` };
  if (area > t.config.area_maxima_m2.min) {
    return { estado: 'avaliacao', motivo: `Para áreas acima de ${t.config.area_maxima_m2.min.toLocaleString('pt-PT')} m² preparamos sempre um orçamento à medida.` };
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
  if (!Number.isInteger(ralos) || ralos < 0) return { estado: 'invalido', motivo: 'Indique o número de ralos (0 se não houver).' };
  if (ralos > t.config.ralos_maximo.min) return { estado: 'avaliacao', motivo: 'Muitos ralos ou pontos de escoamento: precisamos de ver a obra.' };

  const aceites = esc.superficie.regras.filter((r) => r.startsWith('materiais:')).flatMap((r) => r.slice(10).split('|'));
  let mat = esc.material;
  if (mat.chave === 'nao_sei') {
    const op = aceites.map((k) => t.material[k]).filter(Boolean);
    if (!op.length) return { estado: 'avaliacao', motivo: 'Precisamos de ver a obra para indicar a solução.' };
    mat = { min: Math.min(...op.map((o) => o.min)), max: Math.max(...op.map((o) => o.max)) };
  } else if (aceites.length && !aceites.includes(mat.chave)) {
    return { estado: 'invalido', motivo: `${mat.descricao} não é a solução que usamos em ${esc.superficie.descricao.toLowerCase()}. Escolha outro material ou «Não sei».` };
  }

  const extrasM2 = PERGUNTAS.slice(2).map((g) => esc[g]).filter((i) => i.unidade === '€/m²');
  const pct = PERGUNTAS.slice(2).map((g) => esc[g]).filter((i) => i.unidade === '%');
  const iva = t.config.iva_percentagem.min;
  const lado = (l) => {
    const m2 = mat[l] * esc.superficie[l] + extrasM2.reduce((s, i) => s + i[l], 0);
    const fator = pct.reduce((f, i) => f * (1 + i[l] / 100), 1);
    const semIva = (m2 * area + ralos * t.extra.ralo[l]) * fator;
    return { semIva, comIva: semIva * (1 + iva / 100) };
  };
  const a = lado('min');
  const b = lado('max');
  return {
    estado: 'preco',
    area,
    ralos,
    iva,
    m2SemIva: { min: arred(a.semIva / area, 0.5), max: arred(b.semIva / area, 0.5) },
    m2ComIva: { min: arred(a.comIva / area, 0.5), max: arred(b.comIva / area, 0.5) },
    totalSemIva: { min: arred(a.semIva, 10), max: arred(b.semIva, 10) },
    totalComIva: { min: arred(a.comIva, 10), max: arred(b.comIva, 10) },
    notas: PERGUNTAS.map((g) => esc[g]).filter((i) => i.regras.includes('nota')).map((i) => notaDe(i)),
  };
}

function notaDe(i) {
  if (i.chave === 'nao_sei') return `${i.grupo === 'suporte' ? 'Estado do suporte' : 'Remoção'} por confirmar: o intervalo está alargado até vermos fotografias.`;
  if (i.chave === 'ceramico_novo') return 'O pavimento cerâmico novo não está incluído: é orçamentado à parte.';
  if (i.chave === 'levantar_ceramico') return 'Inclui levantar o pavimento existente, não a colocação de pavimento novo.';
  if (i.chave === 'urgente') return 'Com água a entrar, pode ser preciso localizar a origem antes de impermeabilizar.';
  return i.descricao;
}
