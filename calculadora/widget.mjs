/*
 * Calculadora reutilizável (página inicial e /calculadora/).
 * A página tem de ter: <form data-calc-form>, <div data-calc-result>, e os elementos estáticos
 * #calcAcoes e #calcWa (o link de WhatsApp existe no HTML para a medição de cliques do script.js).
 * Opções: data-modo="rapido" (perguntas de afinação fechadas) ou "completo".
 */
import { lerPrecos, calcular, minimoObra } from '/calculadora/motor.mjs?v=20261113-7';

const WA = 'https://wa.me/351930446198?text=';
const ROTULOS = {
  cliente: ['Para quem é a obra?', ''],
  superficie: ['O que vamos impermeabilizar?', ''],
  area: ['Área aproximada (m²)', 'Se tiver várias zonas na mesma morada, some as áreas.'],
  localizacao: ['Onde fica a obra?', ''],
  material: ['Material', 'Se não souber, deixe «Não sei».'],
  suporte: ['Estado da superfície', ''],
  remocao: ['Há sistema antigo a remover?', ''],
  acesso: ['Acesso', ''],
  ralos: ['Número de ralos', ''],
  remates: ['Remates', 'Muretes, soleiras, tubos, claraboias.'],
  isolamento: ['Isolamento térmico', ''],
  acabamento: ['Acabamento final', ''],
  urgencia: ['Prazo', ''],
};
const RAPIDAS = ['cliente', 'superficie', 'area', 'localizacao', 'suporte', 'remocao'];
const AFINAR = ['material', 'acesso', 'remates', 'ralos', 'isolamento', 'acabamento', 'urgencia'];
const DEFEITOS = { material: 'nao_sei', acesso: 'facil', remates: 'normais', ralos: '0', isolamento: 'nao', acabamento: 'sem', urgencia: 'normal' };

const el = (tag, attrs = {}, ...filhos) => { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === 'class') e.className = v; else if (k in e) e[k] = v; else e.setAttribute(k, v); } e.append(...filhos.filter((f) => f !== null && f !== undefined)); return e; };
const eur = (v) => v.toLocaleString('pt-PT', { maximumFractionDigits: 0 }) + ' €';
const intervalo = (o, suf = '') => (o.min === o.max ? eur(o.min) : `${o.min.toLocaleString('pt-PT')} a ${eur(o.max)}`) + suf;

export async function montarCalculadora(raiz) {
  const form = raiz.querySelector('[data-calc-form]');
  const res = raiz.querySelector('[data-calc-result]');
  const acoes = raiz.querySelector('#calcAcoes');
  const wa = raiz.querySelector('#calcWa');
  const mail = raiz.querySelector('#calcEmail');
  const modo = raiz.dataset.modo || 'rapido';
  let t;
  try {
    const r = await fetch('/calculadora/precos.csv?v=20261113-7', { cache: 'no-cache' });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    t = lerPrecos(await r.text());
  } catch (e) {
    res.replaceChildren(el('p', { class: 'calc-aviso calc-stop' }, 'Não foi possível carregar a calculadora. Peça o preço pelo WhatsApp ou ligue 930 446 198.'));
    return;
  }
  const campo = (g) => {
    const [rot, ajuda] = ROTULOS[g];
    let input;
    if (g === 'area' || g === 'ralos') {
      input = el('input', { id: 'c_' + g, name: g, type: 'number', inputMode: g === 'area' ? 'decimal' : 'numeric', min: g === 'area' ? '1' : '0', step: '1', placeholder: g === 'area' ? 'Ex.: 300' : '0' });
    } else {
      input = el('select', { id: 'c_' + g, name: g }, el('option', { value: '' }, 'Escolha'), ...Object.values(t[g]).map((i) => el('option', { value: i.chave }, i.descricao)));
    }
    if (DEFEITOS[g] !== undefined) input.value = DEFEITOS[g];
    return el('div', { class: 'calc-campo' }, el('label', { htmlFor: 'c_' + g }, rot, ajuda ? el('small', {}, ajuda) : null), input);
  };
  const afinar = el('details', { class: 'calc-afinar', open: modo === 'completo' }, el('summary', {}, 'Afinar o preço (opcional)'), el('div', { class: 'calc-grelha' }, ...AFINAR.map(campo)));
  form.replaceChildren(el('div', { class: 'calc-grelha' }, ...RAPIDAS.map(campo)), afinar);
  const pre = new URLSearchParams(location.search);
  for (const k of ['superficie', 'cliente']) if (raiz.dataset[k] && form.elements[k]) form.elements[k].value = raiz.dataset[k];
  for (const k of ['superficie', 'area', 'cliente']) if (pre.get(k) && form.elements[k]) form.elements[k].value = pre.get(k);

  const filtrar = () => {
    const sup = t.superficie[form.elements.superficie.value];
    const aceites = (sup?.regras || []).filter((r) => r.startsWith('materiais:')).flatMap((r) => r.slice(10).split('|'));
    for (const o of form.elements.material.options) { const ok = !o.value || o.value === 'nao_sei' || !aceites.length || aceites.includes(o.value); o.hidden = !ok; o.disabled = !ok; }
    if (form.elements.material.selectedOptions[0]?.disabled) form.elements.material.value = 'nao_sei';
  };
  const desc = (g, d) => t[g][d[g]]?.descricao || '—';
  const mensagem = (d, r) => ['Olá, fiz a estimativa na calculadora do site ImpermeabilizaPro.', '',
    'Cliente: ' + desc('cliente', d), 'Superfície: ' + desc('superficie', d), 'Área: ' + (d.area || '—') + ' m²', 'Localização: ' + desc('localizacao', d),
    'Material: ' + desc('material', d), 'Superfície/suporte: ' + desc('suporte', d), 'Remoção: ' + desc('remocao', d), 'Acesso: ' + desc('acesso', d),
    'Ralos: ' + (d.ralos || 0), 'Remates: ' + desc('remates', d), 'Isolamento: ' + desc('isolamento', d), 'Acabamento: ' + desc('acabamento', d), 'Prazo: ' + desc('urgencia', d), '',
    r ? `Estimativa do site: ${intervalo(r.m2ComIva, '/m²')} · total ${intervalo(r.totalComIva)} ${r.autoliquidacao ? '(sem IVA, autoliquidação)' : 'com IVA'}.` : '',
    'Posso enviar fotografias e a planta/medições.'].join('\n');
  const mostrarAcoes = (d, r) => {
    wa.href = WA + encodeURIComponent(mensagem(d, r));
    if (mail) mail.href = 'mailto:proimpermeabiliza@gmail.com?subject=' + encodeURIComponent(`Pedido de proposta · ${desc('superficie', d)} · ${d.area || '?'} m²`) + '&body=' + encodeURIComponent(mensagem(d, r).replace('Posso enviar fotografias e a planta/medições.', 'Junto em anexo fotografias, planta ou medições.'));
    acoes.hidden = false;
  };
  const escalao = (a) => { const n = Number(String(a).replace(',', '.')); return !n ? 'sem_area' : n < 100 ? '<100' : n < 200 ? '100-199' : n < 500 ? '200-499' : n < 1000 ? '500-999' : '1000+'; };
  let ultimo = '', iniciou = false;
  const medir = (d, r) => {
    if (!iniciou) { iniciou = true; window.dispatchEvent(new CustomEvent('ip:calc', { detail: { tipo: 'inicio' } })); }
    if (r.estado === 'invalido') return;
    const det = { tipo: 'resultado', estado: r.estado, cliente: d.cliente || '', superficie: d.superficie || '', escalao_area: escalao(d.area), localizacao: d.localizacao || '', nao_sei: r.naoSei ?? '', margem: r.margem ?? '' };
    const chave = [det.estado, det.cliente, det.superficie, det.escalao_area].join('|');
    if (chave !== ultimo) { ultimo = chave; window.dispatchEvent(new CustomEvent('ip:calc', { detail: det })); }
  };

  function atualizar() {
    const d = Object.fromEntries(new FormData(form));
    acoes.hidden = true;
    const r = calcular(d, t);
    if (atualizar.interagiu) medir(d, r);
    if (r.estado === 'invalido') {
      const rot = r.falta && ROTULOS[r.falta] ? ROTULOS[r.falta][0] : '';
      res.replaceChildren(el('p', { class: 'calc-vazio' }, d.area || d.cliente || d.superficie ? (rot ? `Falta: ${rot}` : r.motivo) : 'Responda às 6 perguntas para ver o preço por m².'));
      return;
    }
    if (r.estado === 'abaixo_minimo') {
      res.replaceChildren(el('p', { class: 'calc-aviso calc-stop' }, `Trabalhamos em obras a partir de ${r.minimo} m². Para ${d.area} m² não apresentamos preço.`),
        el('p', { class: 'calc-nota' }, `Se houver várias zonas na mesma morada (coberturas, terraços, caves), some as áreas.`));
      return;
    }
    if (r.estado === 'excluido') { res.replaceChildren(el('p', { class: 'calc-aviso calc-stop' }, r.motivo)); return; }
    if (r.estado === 'avaliacao') {
      res.replaceChildren(el('p', { class: 'calc-aviso' }, r.motivo), el('p', { class: 'calc-nota' }, 'Envie fotografias e medidas pelo WhatsApp: respondemos com a solução e o valor.'));
      mostrarAcoes(d, null); return;
    }
    const ivaTxt = r.autoliquidacao ? 'sem IVA · autoliquidação (empresa com IVA dedutível)' : `com IVA (${r.iva}%)` + (d.cliente === 'empresa' ? ' · dedutível para empresas' : '');
    res.replaceChildren(
      el('p', { class: 'calc-rotulo' }, 'Preço estimado por m²'),
      el('p', { class: 'calc-m2' }, intervalo(r.m2ComIva, '/m²')),
      el('p', { class: 'calc-iva' }, ivaTxt),
      el('div', { class: 'calc-linhas' },
        el('p', {}, el('span', {}, `Total para ${r.area.toLocaleString('pt-PT')} m²`), el('b', {}, intervalo(r.totalComIva))),
        r.autoliquidacao ? null : el('p', {}, el('span', {}, d.cliente === 'empresa' ? 'Sem IVA (o que conta para empresas)' : 'Sem IVA'), el('b', {}, intervalo(r.m2SemIva, '/m²')))),
      el('p', { class: 'calc-nota' }, r.naoSei ? `Intervalo de ±${r.margem}%: com ${r.naoSei} resposta(s) «Não sei». Abra «Afinar o preço» para o estreitar.` : `Intervalo de ±${r.margem}%. Valor final confirmado depois de vermos a obra.`),
      ...r.notas.map((n) => el('p', { class: 'calc-nota' }, n)));
    mostrarAcoes(d, r);
  }
  form.elements.superficie.addEventListener('change', filtrar);
  const interagir = () => { atualizar.interagiu = true; atualizar(); };
  form.addEventListener('input', interagir);
  form.addEventListener('change', interagir);
  form.addEventListener('submit', (e) => { e.preventDefault(); atualizar(); });
  document.querySelectorAll('[data-minimo-obra]').forEach((s) => { s.textContent = minimoObra(t); });
  filtrar();
  atualizar();
}

for (const raiz of document.querySelectorAll('[data-calc]')) montarCalculadora(raiz);
