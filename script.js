"use strict";
const PHONE = "351930446198";
const GA4_ID = "G-BBSN5Z50XK";
const ADS_ID = "AW-18418470072";
window.dataLayer = window.dataLayer || [];
window.gtag =
  window.gtag ||
  function () {
    window.dataLayer.push(arguments);
  };
window.gtag("consent", "default", {
  ad_storage: "denied",
  analytics_storage: "denied",
  ad_user_data: "denied",
  ad_personalization: "denied",
  wait_for_update: 500,
});
const params = new URLSearchParams(location.search);
if (
  location.pathname === "/" &&
  ["telhados", "terracos", "paredes"].includes(params.get("servico"))
) {
  const legacy = params.get("servico");
  params.delete("servico");
  location.replace(
    `/${legacy}/${params.size ? "?" + params.toString() : ""}${location.hash}`,
  );
}
const service = document.body.dataset.service || "geral";
const storage = {
  get(key) {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  set(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch {}
  },
};
const CONSENT_LIFETIME = 183 * 24 * 60 * 60 * 1000;
const consentTime = Number(storage.get("ip_consent_at"));
let consent = consentTime && Date.now() - consentTime < CONSENT_LIFETIME ? storage.get("ip_consent") : null;
let attribution = {};
const attributionKeys = [
  "utm_source",
  "utm_medium",
  "utm_campaign",
  "utm_id",
  "utm_term",
  "utm_content",
  "utm_source_platform",
  "utm_creative_format",
  "utm_marketing_tactic",
  "gclid",
  "gbraid",
  "wbraid",
  "dclid",
];
function readAttribution() {
  try {
    attribution = JSON.parse(sessionStorage.getItem("ip_attribution") || "{}");
  } catch {
    attribution = {};
  }
  if (
    !attribution ||
    typeof attribution !== "object" ||
    Array.isArray(attribution)
  )
    attribution = {};
  for (const key of attributionKeys) {
    if (params.has(key)) attribution[key] = params.get(key).slice(0, 250);
  }
  try {
    sessionStorage.setItem("ip_attribution", JSON.stringify(attribution));
  } catch {}
}
function track(event, extra = {}) {
  if (consent !== "accepted") return false;
  const payload = {
    page_path: location.pathname,
    servico: service,
    ...attribution,
    ...extra,
  };
  // Keep the event names already imported into Google Ads as SECONDARY conversions.
  // Clicks are observations, not confirmed contacts; verification_status records this.
  // Send each website event once, directly to this GA4 property.
  window.gtag("event", event, { ...payload, send_to: GA4_ID });
  return true;
}

function claimSessionOnce(key) {
  try {
    if (sessionStorage.getItem(key) === "1") return false;
    sessionStorage.setItem(key, "1");
    return true;
  } catch {
    const fallbackKey = "__" + key.replace(/[^a-z0-9_]/gi, "_");
    if (window[fallbackKey]) return false;
    window[fallbackKey] = true;
    return true;
  }
}
function trackOncePerSession(event, key, extra = {}) {
  if (consent !== "accepted") return false;
  if (!claimSessionOnce(key)) return false;
  return track(event, { ...extra, event_scope: "one_per_session" });
}

function replaceWebsitePhoneNumber(formattedNumber, mobileNumber) {
  if (consent !== "accepted") return;
  const dialNumber = String(mobileNumber || "").replace(/[^+0-9]/g, "");
  if (!/^\+?[0-9]{9,15}$/.test(dialNumber)) return;
  document.querySelectorAll('a[href^="tel:"]').forEach((link) => {
    const current = link.getAttribute("href").replace(/[^0-9]/g, "");
    if (current !== PHONE && current !== "930446198") return;
    link.href = "tel:" + dialNumber;
    // Preserve icons, labels and event handlers. WhatsApp keeps the business number.
    const walker = document.createTreeWalker(link, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      node.nodeValue = node.nodeValue.replace(/(?:\+351\s*)?930\s*446\s*198/g, () => String(formattedNumber));
    }
    const label = link.getAttribute("aria-label");
    if (label) link.setAttribute("aria-label", label.replace(/(?:\+351\s*)?930\s*446\s*198/g, () => String(formattedNumber)));
  });
}

function loadGa4() {
  if (window.__ga4Loaded) return;
  window.__ga4Loaded = true;
  const script = document.createElement("script");
  script.async = true;
  script.src =
    "https://www.googletagmanager.com/gtag/js?id=" +
    encodeURIComponent(GA4_ID);
  document.head.appendChild(script);
  window.gtag("js", new Date());
  window.gtag("config", GA4_ID, {
    send_page_view: true,
    page_path: location.pathname + location.search,
  });
  // Google Ads destination is configured after consent so ad-click attribution
  // can be stored by the Google tag without generating a second page view.
  window.gtag("config", ADS_ID, {
    send_page_view: false,
  });
  // Track connected website calls after consent, using Google's forwarding number.
  window.gtag("config", "AW-18418470072/gM9vCIf3g4UdELiZzs5E", {
    phone_conversion_number: "930 446 198",
    phone_conversion_callback: replaceWebsitePhoneNumber,
  });
}
function applyConsent(value) {
  consent = value;
  const granted = value === "accepted" ? "granted" : "denied";
  window.gtag("consent", "update", {
    ad_storage: granted,
    analytics_storage: granted,
    ad_user_data: granted,
    ad_personalization: granted,
  });
  if (value === "accepted") {
    readAttribution();
    loadGa4();
    // The legacy GTM container is intentionally not loaded here. Tracking is
    // handled directly by the Google tag to avoid duplicate events and old
    // conversion triggers while the container configuration is being retired.
  } else {
    attribution = {};
    try {
      sessionStorage.removeItem("ip_attribution");
    } catch {}
  }
}
const cookie = document.getElementById("cookie");
if (consent === "accepted" || consent === "rejected") applyConsent(consent);
else cookie?.classList.add("show");
function setConsent(value) {
  const revokeLoadedTags = value === "rejected" && window.__ga4Loaded;
  storage.set("ip_consent", value);
  storage.set("ip_consent_at", String(Date.now()));
  applyConsent(value);
  cookie?.classList.remove("show");
  window.dispatchEvent(new Event("ip:consent-panel"));
  if (revokeLoadedTags) {
    // Unload previously consented third-party tags; the next page load keeps GTM blocked.
    document.cookie.split(";").forEach((item) => {
      const name = item.split("=")[0].trim();
      if (!/^(_ga|_gid|_gat|_gcl_)/.test(name)) return;
      const domains = ["", location.hostname, "." + location.hostname];
      for (const domain of domains) document.cookie = `${name}=; Max-Age=0; path=/;${domain ? " domain=" + domain + ";" : ""} SameSite=Lax; Secure`;
    });
    location.reload();
  }
}
document
  .getElementById("accept")
  ?.addEventListener("click", () => setConsent("accepted"));
document
  .getElementById("essential")
  ?.addEventListener("click", () => setConsent("rejected"));
document.getElementById("manageCookies")?.addEventListener("click", () => {
  cookie?.classList.add("show");
  document.getElementById("essential")?.focus();
  window.dispatchEvent(new Event("ip:consent-panel"));
});
const messages = {
  geral: "Olá! Gostaria de pedir um orçamento de impermeabilização.",
  telhados:
    "Olá! Gostaria de pedir um orçamento para impermeabilizar uma cobertura plana.",
  terracos:
    "Olá! Gostaria de pedir um orçamento para impermeabilizar um terraço ou varanda.",
  paredes:
    "Olá! Gostaria de pedir um orçamento para impermeabilizar uma parede.",
  tela:
    "Olá! Gostaria de pedir um orçamento para aplicação de tela asfáltica.",
};
function whatsappUrl(message) {
  return `https://wa.me/${PHONE}?text=${encodeURIComponent(message)}`;
}
document.querySelectorAll(".wa-direct").forEach((link) => {
  link.href = whatsappUrl(messages[service] || messages.geral);
  link.addEventListener("click", () => {
    const placement = link.dataset.placement || "direct";
    trackOncePerSession("ip_whatsapp_click", "ip_whatsapp_click_observed_counted", {
      placement,
      contact_action: "whatsapp",
      measurement_type: "click_to_whatsapp",
      verification_status: "click_only_message_not_confirmed_sent",
    });
    // Direct WhatsApp opens remain a microconversion only.
  });
});
// Include plain WhatsApp links without changing their existing destination/message.
document.querySelectorAll('a[href^="https://wa.me/"]').forEach((link) => {
  if (link.classList.contains("wa-direct") || link.id === "requestLink") return;
  link.addEventListener("click", () => {
    trackOncePerSession("ip_whatsapp_click", "ip_whatsapp_click_observed_counted", {
      placement: link.dataset.placement || "inline_link",
      contact_action: "whatsapp",
      measurement_type: "click_to_whatsapp",
      verification_status: "click_only_message_not_confirmed_sent",
    });
  });
});
document.querySelectorAll('a[href^="tel:"]').forEach((link) =>
  link.addEventListener("click", () => {
    const placement = link.dataset.track || "footer";
    trackOncePerSession("ip_phone_click", "ip_phone_click_observed_counted", {
      placement,
      contact_action: "phone",
      measurement_type: "click_to_call",
      verification_status: "click_only_call_not_confirmed_connected",
    });
    // A click-to-call is not proof of a connected or qualified call.
  }),
);
document
  .querySelectorAll('a[href^="mailto:"]')
  .forEach((link) =>
    link.addEventListener("click", () => {
      trackOncePerSession("ip_email_click", "ip_email_click_observed_counted", {
        contact_action: "email",
        placement: "email_link",
        measurement_type: "click_to_email",
        verification_status: "click_only_email_not_confirmed_sent",
      });
      // A mailto click is observation only, not a primary lead signal.
    }),
  );
document.querySelectorAll(".mobile-menu a").forEach((link) =>
  link.addEventListener("click", () => {
    link.closest("details").open = false;
  }),
);
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape")
    document.querySelectorAll(".mobile-menu[open]").forEach((menu) => {
      menu.open = false;
      menu.querySelector("summary").focus();
    });
});
const form = document.getElementById("quickForm");
if (form) {
  let started = false;
  const markStart = () => {
    if (!started) {
      started = track("form_start", { form_type: "whatsapp_request_builder" });
    }
  };
  form.addEventListener("input", markStart);
  form.addEventListener("change", markStart);
  const error = document.getElementById("formError");
  const status = document.getElementById("requestStatus");
  const requestLink = document.getElementById("requestLink");
  form.addEventListener("input", () => {
    status.hidden = true;
  });
  form.addEventListener("change", () => {
    status.hidden = true;
  });
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    markStart();
    const type = form.elements.tipo;
    const locality = form.elements.localidade;
    const area = form.elements.areaM2;
    [type, locality, area].forEach((field) => {
      field.removeAttribute("aria-invalid");
      field.removeAttribute("aria-errormessage");
    });
    let invalid = null;
    let message = "";
    if (!type.value) {
      invalid = type;
      message =
        "Selecione a superfície. Se não souber, escolha “Não sei, preciso de avaliação”.";
    } else if (!locality.value.trim()) {
      invalid = locality;
      message = "Indique a localidade ou o código postal da obra.";
    } else if (!area.validity.valid) {
      invalid = area;
      message = "Indique uma área superior a zero ou deixe o campo em branco.";
    }
    if (invalid) {
      error.textContent = message;
      error.hidden = false;
      invalid.setAttribute("aria-invalid", "true");
      invalid.setAttribute("aria-errormessage", "formError");
      track("ip_form_validation_error", {
        form_type: "whatsapp_request_builder",
        error_field: invalid.name || invalid.id || "unknown",
      });
      invalid.focus();
      return;
    }
    error.hidden = true;
    const lines = [
      messages[service] || messages.geral,
      `Superfície: ${type.value}`,
      `Localidade: ${locality.value.trim()}`,
      `Situação: ${form.elements.situacao.value}`,
      `Área aproximada: ${area.value ? area.value + " m²" : "Ainda não sei"}`,
    ];
    if (form.elements.cliente?.value) lines.push(`Tipo de cliente: ${form.elements.cliente.value}`);
    const description = form.elements.descricao.value.trim();
    if (description) lines.push(`Detalhes: ${description}`);
    const paidOrigin =
      attribution.gclid || attribution.gbraid || attribution.wbraid
        ? "Google Ads"
        : attribution.utm_source
          ? attribution.utm_source.slice(0, 80)
          : "";
    if (paidOrigin) lines.push(`Origem do pedido: ${paidOrigin}`);
    lines.push("Podem ajudar-me a perceber a solução e preparar um orçamento?");
    const url = whatsappUrl(lines.join("\n"));
    requestLink.href = url;
    status.hidden = false;
    // The click is a microconversion, never proof of a sent message or a received lead.
    track("ip_whatsapp_request_prepared", {
      form_type: "whatsapp_request_builder",
      measurement_type: "message_prepared",
      verification_status: "prepared_not_confirmed_sent",
    });
    trackOncePerSession("ip_whatsapp_click", "ip_whatsapp_click_observed_counted", {
      placement: "request_builder",
      contact_action: "whatsapp",
      measurement_type: "click_to_whatsapp",
      verification_status: "click_only_message_not_confirmed_sent",
    });
    window.open(url, "_blank", "noopener,noreferrer");
  });
  requestLink.addEventListener("click", () => {
    trackOncePerSession("ip_whatsapp_click", "ip_whatsapp_click_observed_counted", {
      placement: "request_fallback",
      contact_action: "whatsapp",
      measurement_type: "click_to_whatsapp",
      verification_status: "click_only_message_not_confirmed_sent",
    });
    // The structured request was already counted on valid form submission.
  });
}

document
  .querySelectorAll('a[href="#pedido"], a[href="/#pedido"]')
  .forEach((link) =>
    link.addEventListener("click", () => {
      const container = link.closest("section, header, footer");
      const placement =
        link.dataset.placement ||
        container?.id ||
        container?.classList?.[0] ||
        "unknown";
      track("ip_quote_cta_click", { placement });
    }),
  );

document.querySelectorAll(".faq-section details").forEach((item, index) => {
  item.addEventListener("toggle", () => {
    if (item.open) track("ip_faq_open", { faq_index: index + 1 });
  });
});

if ("IntersectionObserver" in window) {
  const seenSections = new Set();
  const sectionObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting || seenSections.has(entry.target.id)) return;
        if (track("ip_section_view", { section_id: entry.target.id })) {
          seenSections.add(entry.target.id);
        }
      });
    },
    { threshold: 0.35 },
  );
  document
    .querySelectorAll("main section[id]")
    .forEach((section) => sectionObserver.observe(section));
}

const reachedDepths = new Set();
let depthScheduled = false;
function measureScrollDepth() {
  depthScheduled = false;
  const scrollable = document.documentElement.scrollHeight - innerHeight;
  if (scrollable <= 0) return;
  const depth = Math.round((scrollY / scrollable) * 100);
  [25, 50, 75, 90].forEach((mark) => {
    if (depth >= mark && !reachedDepths.has(mark)) {
      if (track("ip_scroll_depth", { percent_scrolled: mark })) {
        reachedDepths.add(mark);
      }
    }
  });
}
addEventListener(
  "scroll",
  () => {
    if (depthScheduled) return;
    depthScheduled = true;
    requestAnimationFrame(measureScrollDepth);
  },
  { passive: true },
);

const mobileContact = document.getElementById("mobileContact");
const hero = document.querySelector(".hero");
if (mobileContact && hero && "IntersectionObserver" in window) {
  let heroPassed = false;
  const blockers = new Set();
  function render() {
    mobileContact.classList.toggle(
      "is-hidden",
      !heroPassed ||
        blockers.size > 0 ||
        cookie?.classList.contains("show") ||
        !!document.querySelector(".mobile-menu[open]"),
    );
  }
  new IntersectionObserver(
    (entries) => {
      const entry = entries[0];
      heroPassed =
        !entry.isIntersecting && entry.boundingClientRect.bottom <= 0;
      render();
    },
    { threshold: 0 },
  ).observe(hero);
  for (const id of ["pedido", "cta-final"]) {
    const el = document.getElementById(id);
    if (!el) continue;
    new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) blockers.add(id);
        else blockers.delete(id);
        render();
      },
      { threshold: 0 },
    ).observe(el);
  }
  document.querySelector(".mobile-menu")?.addEventListener("toggle", render);
  window.addEventListener("ip:consent-panel", render);
  render();
}

// Client paths keep the same short request and preselect only a non-required field.
document.querySelectorAll("[data-client]").forEach(link => {
  link.addEventListener("click", () => {
    if (form?.elements.cliente) {
      form.elements.cliente.value = link.dataset.client;
      form.dispatchEvent(new Event("change"));
    }
  });
});

// Full-size real photographs, opened on demand without duplicating visible gallery images.
const photos = document.querySelectorAll(".project-card > img, .work-photo > img");
if (photos.length && typeof HTMLDialogElement !== "undefined") {
  const dialog = document.createElement("dialog");
  dialog.className = "photo-dialog";
  dialog.setAttribute("aria-label", "Fotografia da obra");
  const close = document.createElement("button");
  close.type = "button"; close.textContent = "Fechar fotografia";
  const photo = document.createElement("img");
  const caption = document.createElement("p");
  dialog.append(close, photo, caption); document.body.append(dialog);
  close.addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", event => { if (event.target === dialog) dialog.close(); });
  photos.forEach(img => {
    const button = document.createElement("button");
    button.type = "button"; button.className = "photo-open";
    button.setAttribute("aria-label", "Ampliar: " + img.alt);
    img.before(button); button.append(img);
    button.addEventListener("click", () => {
      photo.src = img.src; photo.alt = img.alt; caption.textContent = img.alt;
      dialog.showModal();
      track("ip_work_photo_open", { photo_id: img.src.split("/").pop() });
    });
  });
}

// Close the compact navigation when the visitor returns to the page.
document.addEventListener("click", (event) => {
  const menu = document.querySelector(".mobile-menu[open]");
  if (menu && !menu.contains(event.target)) menu.open = false;
});


// Optional callback form: sends a prefilled WhatsApp request for visitors who prefer a phone call.
const callbackForms = document.querySelectorAll(".callback-form");
callbackForms.forEach((callbackForm) => {
  const status = callbackForm.querySelector(".callback-status");

  callbackForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!callbackForm.reportValidity()) return;

    const rawPhone = String(callbackForm.elements.telefone?.value || "").trim();
    const phoneDigits = rawPhone.replace(/\D/g, "");
    const locality = String(callbackForm.elements.localidade_callback?.value || "").trim();

    if (phoneDigits.length < 9) {
      status.hidden = false;
      status.textContent = "Confirme o número de telemóvel.";
      callbackForm.elements.telefone?.focus();
      return;
    }

    const lines = [
      "Olá, prefiro que me liguem para dar seguimento ao meu pedido.",
      "",
      "Telemóvel: " + rawPhone,
      locality ? "Localidade: " + locality : "",
    ].filter(Boolean);

    if (attribution.gclid || attribution.gbraid || attribution.wbraid) {
      lines.push("", "Origem do pedido: Google Ads");
    }

    const whatsappUrl =
      "https://wa.me/" + PHONE + "?text=" + encodeURIComponent(lines.join("\n"));

    // Use the same imported secondary event and session key as other WhatsApp opens.
    trackOncePerSession("ip_whatsapp_click", "ip_whatsapp_click_observed_counted", {
      placement: "callback_request",
      contact_action: "whatsapp",
      measurement_type: "click_to_whatsapp",
      verification_status: "click_only_message_not_confirmed_sent",
    });

    track("ip_callback_whatsapp_open", {
      form_type: "callback_request",
      contact_action: "whatsapp",
      measurement_type: "click_only_message_not_confirmed_sent",
      verification_status: "whatsapp_opened_not_message_confirmed",
    });

    status.hidden = false;
    status.textContent = "A mensagem está preparada. Confirme o envio no WhatsApp para recebermos o pedido.";
    window.open(whatsappUrl, "_blank", "noopener,noreferrer");
  });
});


// Homepage hero slider: serve local images and allow more time to read the hero.
const heroSlideImage = document.getElementById("heroSlideImage");
if (heroSlideImage) {
  const heroImagePaths = [
    "/assets/foto-real-20260915-162914-hero.webp",
    "/assets/foto-real-20260915-162859-hero.webp",
    "/assets/caso-aroeira-3000m2.webp",
    "/assets/foto-real-20260915-161418-hero.webp",
    "/assets/foto-real-20260915-161929-hero.webp",
    "/assets/foto-real-20260909-151643-hero.webp",
  ];
  const heroImageAlts = [
    "Cobertura real impermeabilizada com tela asfáltica",
    "Execução real de impermeabilização numa cobertura",
    "Impermeabilização real de paredes enterradas numa obra",
    "Detalhe real de trabalho de impermeabilização",
    "Aplicação real de impermeabilização numa cobertura",
    "Execução real de impermeabilização em obra",
  ];
  const heroDots = [...document.querySelectorAll(".hero-background-footer .hero-dot")];
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const loadedHeroImages = new Set();
  let heroImageIndex = 0;
  let heroImageTimer = null;

  function heroImageUrl(path) {
    return path;
  }

  function preloadHeroImage(index) {
    const normalized = (index + heroImagePaths.length) % heroImagePaths.length;
    if (loadedHeroImages.has(normalized)) return;
    loadedHeroImages.add(normalized);
    const preload = new Image();
    preload.decoding = "async";
    preload.src = heroImageUrl(heroImagePaths[normalized]);
  }

  function renderHeroImage(index, animate = true) {
    heroImageIndex = (index + heroImagePaths.length) % heroImagePaths.length;
    const nextSrc = heroImageUrl(heroImagePaths[heroImageIndex]);

    const apply = () => {
      heroSlideImage.src = nextSrc;
      heroSlideImage.alt = "";
      heroSlideImage.classList.add("is-active");
      heroDots.forEach((dot, dotIndex) => {
        const active = dotIndex === heroImageIndex;
        dot.classList.toggle("is-active", active);
        if (active) dot.setAttribute("aria-current", "true");
        else dot.removeAttribute("aria-current");
      });
      if (heroImageIndex !== 0) preloadHeroImage(heroImageIndex + 1);
      requestAnimationFrame(() => heroSlideImage.classList.remove("is-changing"));
    };

    if (!animate || reduceMotion) {
      apply();
      return;
    }

    heroSlideImage.classList.add("is-changing");
    setTimeout(apply, 260);
  }

  function stopHeroImages() {
    if (heroImageTimer) clearInterval(heroImageTimer);
    heroImageTimer = null;
  }

  function startHeroImages() {
    stopHeroImages();
    if (reduceMotion || document.hidden) return;
    // Give the primary hero image time to load before preloading the next slide.
    heroImageTimer = setInterval(
      () => renderHeroImage(heroImageIndex + 1),
      6000,
    );
  }

  heroDots.forEach((dot, index) => {
    dot.addEventListener("click", () => {
      preloadHeroImage(index);
      renderHeroImage(index);
      startHeroImages();
    });
  });

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stopHeroImages();
    else startHeroImages();
  });

  loadedHeroImages.add(0);
  renderHeroImage(0, false);
  startHeroImages();
}



