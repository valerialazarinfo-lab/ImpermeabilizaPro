# Website decisions

## User decision — 17 September 2026

No Tally forms or external form integrations. Questions stay on the website. Answers build a WhatsApp message to +351 930 446 198. The visitor reviews and sends it in WhatsApp. Opening WhatsApp must never be represented as a submitted form or a confirmed lead.

Keep this decision when making future edits. It supersedes the older master briefing's recommendation for a Tally or independent lead form.

## Conversion work — 17 September 2026

- Home, roof and terrace pages use specific service headings, real existing photography, visible geographical coverage and direct phone contact.
- Sequence: service promise, trust signals, work photography, request, situations/services, technical explanation, process, named contact, FAQ, final action.
- Request requires only surface and locality; situation defaults to unknown, area and details are optional. Roof/terrace pages preselect the corresponding surface.
- WhatsApp is explicitly named in the principal hero action and final submit button. Keep a visible retry link after preparing a message in case a new tab is blocked. Never display “request received”.
- No new ratings, guarantees, years of experience, completed-job quantities or case histories were invented. Existing photography is only 640×360: do not upscale it into a claimed high-resolution portfolio.
- Analytics emits one canonical phone or WhatsApp click event per action. Request preparation is diagnostic; no form-submitted or lead-success event is emitted. User-written details and locality never enter the dataLayer.
- Tag Manager loads after analytics/advertising consent. Denied visitors can still use every contact function. Storage failures must not break contacts.

## Competitors consulted

- https://www.monocapa.pt/ — service-specific navigation, portfolio, company identity and direct contacts. Applied: explicit service headings and clear identity/contact details. Did not copy their credentials or history.
- https://pom-lda.pt/ — prominent request, staged explanation of the work and services. Applied: understandable next steps and mobile navigation. Did not adopt their guarantee or numerical claims.
- https://impermeabilizar.pt/ — service, geography, quote CTA and FAQ coverage. Applied: visible scope, cost factors and contact choice; avoid excessive claims and repeated pressure.

These are qualitative design comparisons, not measured conversion-rate rankings. The new website cannot honestly be labelled “100% converting” or proven superior without traffic and lead-quality evidence.

## Operational follow-up

- Check which GTM/Ads triggers currently use ip_whatsapp_click and ip_phone_click; the website update does not alter an Ads account or validate that account's conversion settings.
- Assess real sent messages, qualified requests and accepted quotes. A WhatsApp click alone is not a lead.
- Add higher-resolution original photographs and verified reviews when available. Do not fabricate missing evidence.
- No live test message was sent to the business during the code tests.

## Verification and recovered issue

Automated DOM tests passed on all three landing pages: required fields, preselected service, optional/decimal/invalid area, WhatsApp URL encoding, blocked-popup fallback, consent gating, storage failures, no personal answers in analytics and no false lead events. Structural checks passed for anchors, labels and referenced assets. GitHub Pages deployed successfully; desktop hero, live validation, roof and terrace pages were inspected. No message was sent. Full mobile-device and Safari verification remains outstanding because the available browser did not support the attempted mobile viewport preview.

The inherited assets/vinicius-nascimento.webp is invalid (both browser display and image decoder verification failed; historical versions were also invalid). The visible broken portrait was replaced by a named contact panel with initials and telephone/WhatsApp. Restore photography only from a valid original. The old binary is retained for possible recovery and is not referenced by the pages.

## User corrections — 18 September 2026

- Portfolio now uses compact four-column desktop cards, two-column tablet cards and bounded mobile cards. Card text contrast fixed. Full-size originals can be opened in an accessible native dialog. Existing 1200px images preserved without artificial upscaling.
- Valid 720×900 Vinícius portrait is now larger, centered and shown as a 4:5 portrait. The older invalid-image note above is superseded by the valid assets in the current repository.
- Roof gallery now uses obra-real-cobertura-02.webp; hero retains hero-telhados-real.webp. The old gallery file was another encoding/crop of the hero photograph.
- Home remains focused on household needs, with distinct Particular and Business/Condominium sections leading into the same short WhatsApp builder. Client type is optional.
- Footer has legible privacy, cookies, preference management, legal/contact and official complaints-portal links. Logo's exterior white square is visually clipped; original artwork is preserved.
- Privacy expanded with purposes, rights/CNPD, storage, third-party services and withdrawal. No NIF published. Legal completeness is NOT certified: legal operator identity/address, applicable arbitration entity and specific electronic complaints registration still need business confirmation. The portal link is general, not proof of registration.
- Consent expires after 183 days. Withdrawal clears first-party Google cookie names and reloads to unload already-loaded tags. No third-party tags before consent. Removed pre-consent Google preconnect.
- Canonical URLs and existing GTM ID preserved. Intrinsic image dimensions corrected. Service/breadcrumb JSON-LD and legal-page metadata added. No fabricated reviews or guarantees.
- Validation: local assets/links/anchors, unique IDs, one H1 per page, JSON-LD parsing and JavaScript syntax pass. VM checks pass for no-consent blocking, consent expiry/withdrawal, storage failure, WhatsApp client type, exclusion of personal form answers from analytics and absence of false form-submission events. No business message sent.
- Live GA4/Ads conversion configuration and Search Console coverage are not verified by these code tests. Real-device/mobile rendering remains a separate verification item.


## Corporate presentation — 18 September 2026

- Published a consistent navy hero, quieter borders, clearer typography, compact real-work cards and simpler navigation across home, roofs and terraces. Preserved the four original project photographs and service-specific images.
- Increased the valid portrait to 224×280 desktop / 200×250 mobile, centered without artificial image enhancement.
- Improved text contrast and secondary text sizes, responsive spacing, cookie-panel overflow, active service navigation and outside-click menu closure. Native photo dialogs now lock background scrolling.
- Preserved contact numbers, WhatsApp preparation, the existing GA4/GTM configuration, consent behavior, canonical .pt URLs and all legal-page content. No Google Ads campaigns changed.
- Validation: structural checks for all three landing pages (assets, anchors, IDs, one H1 and JSON-LD), JavaScript syntax, successful GitHub Pages deployment, live desktop visual review, gallery open/close, required-field validation and service preselection. No business messages sent.
- Cloud browser cannot access the local preview and does not expose viewport resizing. Responsive CSS was updated, but a real mobile-device visual check is still outstanding.
- The prior legal/operator-data and live Ads/analytics configuration follow-ups remain outstanding; this design revision does not certify those.

## Tracking audit and access-transfer attempt — 18 September 2026

- Confirmed repository CNAME, canonical URLs, sitemap and active ad destinations use impermeabilizapro.pt. Do not revert to the older .blog domain.
- Connected reporting sources: Ads 396-652-0841, GA4 property 554830576, Search Console https://impermeabilizapro.pt/. Reporting connectivity does not establish administrator access or corporate ownership.
- Corporate account requested: proimpermeabiliza@gmail.com. No access transfer was completed: Google Tag Manager and Google Ads administration returned 502 Connection refused in this session. Preserve existing personal access until corporate administrator/publish access is verified.
- Ads campaign 24188606637 uses manual CPC, location PRESENCE, no Display and no Search partners. Existing negatives already exclude many material/product/tutorial searches. No budgets, bids, campaigns or exclusions were changed during this audit.
- Reporting for 2026-09-11 through 2026-09-18: 150 impressions, 24 clicks, 27.45 account-currency spend, 1 conversion under the historical “Pedido de Avaliação Enviado” label. The conversion settings response marks that action secondary; historical conversions may predate that change. Do not treat this metric as a confirmed received quote request.
- GA4 reporting returns page views, form_start, ip_whatsapp_click, scroll and section events. End-to-end GTM Preview, Ads conversion firing and duplicate-GA4-tag checks remain unverified.
- Fixed script.js: direct gtag custom events explicitly target G-BBSN5Z50XK; GTM dataLayer events remain available. Form start, section and scroll milestones are marked counted only after consent permits tracking. A later eligible interaction can therefore be recorded. Email and WhatsApp retry actions now participate in the existing one-per-session contact-intent counter.
- Syntax/diff checks and Node VM behavior tests passed: consent gating, late consent, form/scroll/section counts, cross-channel contact-intent deduplication, blocked storage, explicit GA4 destination, WhatsApp URL construction and exclusion of personal form answers from analytics. No message was sent. These code tests do not prove live tag delivery.
- Remaining administration work: verify company administrators on GTM, Ads, GA4 and Search Console; inspect live GTM triggers and rename obsolete submitted-request conversion terminology; verify primary/secondary conversion goals and duplicate imports; validate in Preview before publishing GTM changes. Domain/DNS ownership was not inspected.


## Tracking final cleanup — 19 September 2026

- Live website tracking now uses the direct Google tag only: GA4 `G-BBSN5Z50XK` plus Google Ads destination `AW-18418470072`, loaded only after analytics/advertising consent.
- Legacy GTM container `GTM-KTCT795B` is no longer loaded by the website. This prevents old GTM triggers and duplicate GA4/custom conversion firing from affecting live measurement.
- Contact measurement is channel-specific and truthful: `ip_whatsapp_click` means click-to-open WhatsApp, `ip_phone_click` means click-to-call, and `ip_email_click` means click-to-email. None of these claims a sent message, connected call, sent email, or confirmed lead.
- `ip_contact_intent` remains a one-per-session aggregate of the first contact-channel click. `ip_whatsapp_request_prepared` means only that the website prepared a WhatsApp message.
- WhatsApp, phone and email channel click events are each deduplicated once per session. Form validation, quote CTA, section, FAQ and scroll diagnostics remain non-lead events.
- Google Ads auto-tagging is confirmed enabled. The old Google Ads action “Pedido de Avaliação Enviado” is still present in the account as a secondary website conversion, but the live website no longer loads the legacy GTM path that could trigger it and does not emit a submitted/received-lead event.
- The current Google Ads connector supports campaign/ad mutations but does not expose conversion-action rename/remove or GA4 key-event administration. Those account-admin changes therefore remain outside this connector's writable scope.

## Conversion cleanup — 25 September 2026

- Removed emission of `ip_contact_intent` from the live website because it is an aggregate click-intent signal, not a confirmed lead, and Google Ads had counted it in the Conversions column.
- Kept `ip_whatsapp_click`, `ip_phone_click` and `ip_email_click` as channel-specific observation events only. They do not claim a sent message, connected call or sent email.
- Kept `ip_whatsapp_request_prepared` and callback-open events as diagnostics only.
- Refreshed the tracking script cache reference on Home, Telhados, Terraços, Paredes and Tela Asfáltica so the corrected bundle is loaded.
- Google Ads account-level call reporting remains enabled and the call asset uses +351 930 446 198. Website-call conversion tracking with a Google forwarding number still requires a dedicated Google Ads conversion action/snippet and is not writable through the current connector.

## Observed-contact event names — 25 September 2026

- Renamed website click events to `ip_whatsapp_click_observed`, `ip_phone_click_observed` and `ip_email_click_observed`.
- Purpose: prevent historic GA4/Google Ads key-event or conversion configurations attached to the old event names from continuing to receive simple click/open signals as if they were confirmed contacts.
- Historical data is preserved under the old names. New observed events remain available for funnel analysis but are not lead-success events.
- `ip_contact_intent` remains removed from live tracking.
- Confirmed contact conversions should be created from connected/qualified calls or imported real leads (WhatsApp, email, SMS, quote request) rather than from button clicks.

## SEO local, entidade única e pesquisa por IA — 13 de novembro de 2026

- `scripts/seo_build.py` é a fonte única dos dados públicos da empresa para SEO. Correr `python3 scripts/seo_build.py` depois de editar páginas; é idempotente (verificado com duas execuções seguidas sem diferenças).
- Todas as páginas indexáveis partilham a mesma entidade `HomeAndConstructionBusiness` (`https://impermeabilizapro.pt/#negocio`) com Person (Vinícius Nascimento), WebSite, WebPage e BreadcrumbList. Os `Service` passam a apontar para essa entidade. Removidos os blocos de empresa duplicados e diferentes entre páginas (auditoria A22).
- Sem morada de rua, horário, avaliações, preços, garantias ou certificações: só localidade-base (Sobral de Monte Agraço), contactos e ficha do Google Maps já publicados.
- Nova página `/impermeabilizacao-sobral-de-monte-agraco/` (localidade-base da ficha Google Maps).
- Páginas locais com conteúdo próprio: freguesias/localidades, contexto técnico geral e FAQ visível + FAQPage. Sem obras ou números inventados; a Ericeira usa a obra real já publicada.
- Bloco de ligações internas (serviços, zonas, guias, contacto) em todas as páginas; páginas sem rodapé passam a ter ligações legais. Open Graph e canonical acrescentados onde faltavam.
- `sitemap.xml` gerado (18 URLs, inclui simulador e Sobral; páginas legais e `/telhados/` ficam fora). `llms.txt` criado para assistentes de IA, incluindo o que NÃO é feito (telhados de telha/inclinados, grande altura).
- Imagem principal (LCP) em WebP 1440px: 482 KB → 182 KB; slider da homepage com as mesmas fotos em WebP. Originais JPEG preservados (og:image continua JPEG). Cache de `script.js` atualizado.
- Verificado localmente: JSON-LD válido, 1 H1, 1 canonical, sem IDs duplicados nem ligações internas partidas em 21 páginas; sem overflow horizontal em iPhone 13 e 1366px; sem erros JS. Não verificado: publicação no domínio (rede bloqueada nesta sessão), Search Console, Rich Results Test e Core Web Vitals reais.

## Perfil da Empresa no Google — 13 de novembro de 2026

- A ficha é gerida pela conta proimpermeabiliza@gmail.com (validada, só área de serviço, morada oculta). A conta lazarvaleria632 não tem acesso; os relatórios mensais chegam a valerialazarinfo@gmail.com.
- Alterado pela Valeria com o Claude no Chrome: descrição nova sem telhados, link do site com `utm_source=google&utm_medium=organic&utm_campaign=gbp`, categorias secundárias "Empreiteiro" e "Serviço de reparação de danos causados pela água", 7 serviços iguais aos do site (removidos "telhados e coberturas", prevenção, renovação, manutenção). Área de serviço: 13 concelhos, incluindo Amadora. Horário (08:00 às 22:00, todos os dias) por confirmar com o Vinícius.
- O site usa a mesma lista de 13 concelhos em `areaServed` (`GBP_AREAS` em `scripts/seo_build.py`).
- Ponto de partida (relatório Google, outubro de 2026): 67 visualizações, 1 visita ao site, 0 chamadas, 0 cliques no chat. Indicador principal: chamadas + visitas ao site a partir da ficha.
- Publicações da ficha (13-11-2026): nova publicação aprovada e visível, sem telhados, com botão "Ligar agora" (930 446 198). Eliminadas (13-11-2026, texto confirmado antes de apagar) as duas antigas que anunciavam telhados (o Google não tem "Arquivar"). Início dos textos eliminados, para histórico: "Tem infiltrações num telhado, terraço, parede ou cobertura? Na ImpermeabilizaPro avaliamos a…" (2-10-2026) e "Infiltrações em terraços, telhados, varandas ou paredes? A ImpermeabilizaPro executa trabalhos…".
- Fotos da ficha (13-11-2026): a Valeria carregou 10 fotos reais de obra (JPG com nomes descritivos). Apagadas 3 cópias exatas (2 da parede com pinheiros, 1 da cobertura estreita com trabalhador), verificadas uma a uma. Mantidos pares com enquadramentos diferentes. Por fazer: quando as 2 fotos em "Pending" forem aprovadas, apagar as 2 versões antigas do terraço com clarabóia. Categorias e 7 serviços visíveis, sem rejeição. Data de abertura "maio de 2020" (não preenchida nesta sessão) por confirmar pela Valeria.
- Horário 08:00–22:00 todos os dias confirmado pela Valeria (13-11-2026). Data de abertura: não é para preencher nem alterar; fica como o Google a tem.

## Novas páginas — 13 de novembro de 2026

- 7 páginas de zona para os concelhos da ficha Google sem página: Arruda dos Vinhos, Alenquer, Vila Franca de Xira, Odivelas, Amadora, Lourinhã, Cadaval. Conteúdo próprio por concelho (freguesias, contexto técnico geral, FAQ). Sem obras ou números inventados.
- Página `/obras/` com as 4 obras reais já publicadas (Ericeira, Gaia, Aroeira, Ílhavo), só com os factos que já estavam no site. Aroeira mantém "em execução"; não indicado concelho nem estado das outras por não estar confirmado.
- Sitemap passa a 26 URLs. Verificado: JSON-LD, 1 H1, canonical, ligações internas, sem overflow em telemóvel e 1366px, script idempotente.
- Link de avaliação Google (13-11-2026): https://g.page/r/CSxqX6SG4QDvEBM/review, também no bloco de contacto de todas as páginas.
