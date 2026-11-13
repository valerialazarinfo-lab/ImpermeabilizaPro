import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { lerPrecos, calcular, minimoObra } from './motor.mjs';

const csv = readFileSync(new URL('./precos.csv', import.meta.url), 'utf8');
const t = lerPrecos(csv);
const base = { superficie: 'cobertura_plana', area: 150, material: 'tela_2', suporte: 'bom', remocao: 'nenhuma', acesso: 'facil', ralos: 2, remates: 'normais', isolamento: 'nao', acabamento: 'sem', urgencia: 'normal', localizacao: 'zona_base' };

test('mínimo de obra lido do CSV', () => assert.equal(minimoObra(t), 100));

test('caso base: 150 m² de cobertura com tela dupla', () => {
  const r = calcular(base, t);
  assert.equal(r.estado, 'preco');
  // (30+2)×150 + 2×40 = 4880 ; (42+4)×150 + 2×90 = 7080 ; ×1,23
  assert.deepEqual(r.totalSemIva, { min: 4880, max: 7080 });
  assert.deepEqual(r.totalComIva, { min: 6000, max: 8710 });
  assert.ok(r.m2ComIva.min < r.m2ComIva.max);
  assert.equal(r.iva, 23);
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

test('telhado inclinado e grande altura: excluídos', () => {
  assert.equal(calcular({ ...base, superficie: 'telhado_inclinado' }, t).estado, 'excluido');
  assert.equal(calcular({ ...base, acesso: 'grande_altura' }, t).estado, 'excluido');
});

test('andaime e fora da zona: avaliação sem preço', () => {
  assert.equal(calcular({ ...base, acesso: 'andaime' }, t).estado, 'avaliacao');
  assert.equal(calcular({ ...base, localizacao: 'fora' }, t).estado, 'avaliacao');
});

test('material incompatível com a superfície é recusado', () => {
  assert.equal(calcular({ ...base, superficie: 'casa_banho', material: 'tela_2' }, t).estado, 'invalido');
});

test('«Não sei» usa o intervalo dos materiais aceites', () => {
  const r = calcular({ ...base, material: 'nao_sei' }, t);
  const tela1 = calcular({ ...base, material: 'tela_1' }, t);
  const tela2 = calcular({ ...base, material: 'tela_2' }, t);
  assert.ok(r.totalSemIva.min <= tela1.totalSemIva.min && r.totalSemIva.max >= tela2.totalSemIva.max);
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

test('CSV com valores errados falha de forma clara', () => {
  assert.throws(() => lerPrecos(csv.replace('tela_1;Tela asfáltica, 1 camada;22;32', 'tela_1;Tela asfáltica, 1 camada;40;32')), /inválidos/);
});
