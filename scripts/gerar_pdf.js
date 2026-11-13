// Gera assets/apresentacao-impermeabilizapro.pdf a partir de /apresentacao/ (corre depois de gerar_paginas.py).
// Uso: node scripts/gerar_pdf.js
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const raiz = path.resolve(__dirname, '..');
const tipos = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.webp': 'image/webp', '.jpeg': 'image/jpeg', '.png': 'image/png' };
const srv = http.createServer((q, r) => { let p = decodeURIComponent(q.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html'; const f = path.join(raiz, p); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'content-type': tipos[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0, async () => {
  const b = await chromium.launch(); const pg = await b.newPage();
  await pg.goto(`http://localhost:${srv.address().port}/apresentacao/`, { waitUntil: 'networkidle' });
  await pg.pdf({ path: path.join(raiz, 'assets/apresentacao-impermeabilizapro.pdf'), format: 'A4', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  await b.close(); srv.close(); console.log('PDF gerado: assets/apresentacao-impermeabilizapro.pdf');
});
