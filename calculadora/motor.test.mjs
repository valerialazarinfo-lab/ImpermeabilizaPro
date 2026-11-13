import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { lerPrecos, calcular, minimoObra, fatorEscala } from './motor.mjs';

const csv = readFileSync(new URL('./precos.csv', import.meta.url), 'utf8');
const t = lerPrecos(csv);
const base = { cliente: 'condominio', superficie: 'cobertura_plana', area: 150, material: 'tela_2', fornecimento: 'nos', suporte: 'bom', remocao: 'nenhuma', acesso: 'facil', ralos: 2, remates: 'normais', isolamento: 'nao', acabamento: 'sem', urgencia: 'normal', localizacao: 'zona_base' };

test('mínimo de obra lido do CSV', () => assert.equal(minimoObra(t), 100));

test('caso base: intervalo estreito (±5%) com IVA para condomínio', () => {
  const r = calcular(base, t);
  assert.equal(r.estado, 'preco');
  // médio: ((36 + 3) €/m² × 150 + 2 × 65) × 1 = 5980 € s/IVA
  assert.equal(r.margem, 5);
  assert.deepEqual(r.totalSemIva, { min: 5700, max: 6300 });
  assert.equal(r.iva, 23);
  assert.deepEqual(r.m2ComIva, { min: 47, max: 51 });
  assert.ok(r.m2ComIva.max - r.m2ComIva.min <= 5, 'intervalo por m² estreito');
});

test('empresa sem habilitação IMPIC: IVA 23% (sem autoliquidação)', () => {
  const r = calcular({ ...base, cliente: 'empresa' }, t);
  assert.equal(r.autoliquidacao, false);
  assert.equal(r.iva, 23);
});

test('empresa com autoliquidação ativa: preço sem IVA', () => {
  const t1 = lerPrecos(csv.replace(/config;autoliquidacao_ativa;([^;]*);0;0/, 'config;autoliquidacao_ativa;$1;1;1'));
  const r = calcular({ ...base, cliente: 'empresa' }, t1);
  assert.equal(r.autoliquidacao, true);
  assert.equal(r.iva, 0);
  assert.deepEqual(r.m2ComIva, r.m2SemIva);
  assert.equal(calcular(base, t1).iva, 23, 'condomínio continua com IVA');
});

test('«Não sei»: mínimo = tudo bom, máximo = pior caso', () => {
  const ns = calcular({ ...base, suporte: 'nao_sei', remocao: 'nao_sei' }, t);
  const bom = calcular({ ...base, suporte: 'bom', remocao: 'nenhuma' }, t);
  const pior = calcular({ ...base, suporte: 'degradado', remocao: 'tela_antiga' }, t);
  assert.equal(ns.naoSei, 2);
  assert.equal(ns.totalSemIva.min, bom.totalSemIva.min);
  assert.ok(ns.totalSemIva.max >= pior.totalSemIva.max, 'o máximo cobre o pior caso');
});

test('economia de escala: €/m² desce com a área', () => {
  const pm = (area) => calcular({ ...base, ralos: 0, area }, t).totalSemIva.max / area;
  const a = pm(150), b = pm(600), c = pm(2000);
  assert.ok(a > b && b > c, `${a} > ${b} > ${c}`);
  assert.equal(fatorEscala(99, t), 1);
  assert.equal(fatorEscala(1000, t), 0.97);
});

test('abaixo do mínimo não dá preço', () => {
  const r = calcular({ ...base, area: 99 }, t);
  assert.equal(r.estado, 'abaixo_minimo');
  assert.equal(r.totalComIva, undefined);
});

test('exatamente no mínimo dá preço', () => assert.equal(calcular({ ...base, area: 100 }, t).estado, 'preco'));

test('mínimo de 200 m² (alteração no CSV) bloqueia 150 m²', () => {
  const t200 = lerPrecos(csv.replace(/config;minimo_obra_m2;([^;]*);100;100/, 'config;minimo_obra_m2;$1;200;200'));
  assert.equal(calcular(base, t200).estado, 'abaixo_minimo');
  assert.equal(calcular({ ...base, area: 200 }, t200).estado, 'preco');
});

test('área inválida, vazia ou negativa', () => {
  for (const area of ['', 'abc', -5, 0]) assert.equal(calcular({ ...base, area }, t).estado, 'invalido');
});

test('aceita vírgula decimal', () => assert.equal(calcular({ ...base, area: '120,5' }, t).estado, 'preco'));

test('falta o tipo de cliente: indica a pergunta', () => {
  const r = calcular({ ...base, cliente: '' }, t);
  assert.equal(r.estado, 'invalido');
  assert.equal(r.falta, 'cliente');
});

test('telhado inclinado e grande altura: excluídos', () => {
  assert.equal(calcular({ ...base, superficie: 'telhado_inclinado' }, t).estado, 'excluido');
  assert.equal(calcular({ ...base, acesso: 'grande_altura' }, t).estado, 'excluido');
});

test('andaime e fora da zona: avaliação sem preço', () => {
  assert.equal(calcular({ ...base, acesso: 'andaime' }, t).estado, 'avaliacao');
  assert.equal(calcular({ ...base, localizacao: 'fora' }, t).estado, 'avaliacao');
});

test('material incompatível com a superfície é recusado', () => {
  assert.equal(calcular({ ...base, superficie: 'parede_exterior', material: 'tela_2' }, t).estado, 'invalido');
});

test('casa de banho: serviço à parte, sem preço e sem mínimo', () => {
  const r = calcular({ ...base, superficie: 'casa_banho', area: 8 }, t);
  assert.equal(r.estado, 'avaliacao');
  assert.match(r.motivo, /serviço à parte/);
});

test('cada agravamento sobe o preço', () => {
  const ref = calcular(base, t).totalComIva.max;
  for (const [k, v] of [['suporte', 'degradado'], ['remocao', 'tela_antiga'], ['acesso', 'escadas'], ['remates', 'muitos'], ['isolamento', 'xps'], ['acabamento', 'protecao_pesada'], ['urgencia', 'urgente'], ['localizacao', 'outros_distritos'], ['ralos', 6]]) {
    assert.ok(calcular({ ...base, [k]: v }, t).totalComIva.max > ref, `${k}=${v}`);
  }
});

test('ralos inválidos ou em excesso', () => {
  assert.equal(calcular({ ...base, ralos: -1 }, t).estado, 'invalido');
  assert.equal(calcular({ ...base, ralos: 2.5 }, t).estado, 'invalido');
  assert.equal(calcular({ ...base, ralos: 50 }, t).estado, 'avaliacao');
});

test('área acima do máximo automático vai para avaliação', () => assert.equal(calcular({ ...base, area: 5000 }, t).estado, 'avaliacao'));

test('todas as linhas têm origem', () => {
  for (const g of Object.values(t)) for (const i of Object.values(g)) assert.ok(i.origem.length > 5, `${i.grupo}/${i.chave}`);
});

test('fator de preço de entrada reduz o preço', () => {
  const t1 = lerPrecos(csv.replace(/config;fator_preco_entrada;([^;]*);1;1/, 'config;fator_preco_entrada;$1;0,9;0,9'));
  assert.ok(calcular(base, t1).totalSemIva.max < calcular(base, t).totalSemIva.max);
});

test('só mão de obra: preço do sistema × 0,53, extras iguais', () => {
  const com = calcular({ ...base, ralos: 0, remates: 'poucos' }, t);
  const mo = calcular({ ...base, ralos: 0, remates: 'poucos', fornecimento: 'cliente' }, t);
  assert.equal(mo.estado, 'preco');
  assert.ok(Math.abs(mo.totalSemIva.max / com.totalSemIva.max - 0.53) < 0.02);
  assert.ok(mo.notas.some((n) => /Só mão de obra/.test(n)));
});

test('CSV com valores errados falha de forma clara', () => {
  assert.throws(() => lerPrecos(csv.replace('tela_1;Tela asfáltica, 1 camada;22;32', 'tela_1;Tela asfáltica, 1 camada;40;32')), /inválidos/);
});
