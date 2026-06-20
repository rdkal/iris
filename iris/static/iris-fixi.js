// iris-fixi.js — first-party extension for fixi (https://github.com/bigskysoftware/fixi).
// Adds the pieces fixi deliberately omits, using only fixi's event API:
//   - loading indicators  (toggle .fx-loading during a request)
//   - history / push-url  (fx-push-url -> pushState; popstate re-requests)
//   - polling             (fx-poll="2s" re-triggers on an interval)
(() => {
  if (window.__iris_fixi) return;
  window.__iris_fixi = true;

  // --- Loading indicators ------------------------------------------------
  const mark = (e, on) => {
    const { cfg } = e.detail;
    const toggle = (el) => el && el.classList && el.classList[on ? "add" : "remove"]("fx-loading");
    toggle(e.target);
    toggle(cfg && cfg.target);
  };
  document.addEventListener("fx:before", (e) => mark(e, true));
  document.addEventListener("fx:finally", (e) => mark(e, false));

  // --- History / push-url ------------------------------------------------
  // Mark requests whose element opts in, then push after a successful swap.
  document.addEventListener("fx:config", (e) => {
    const el = e.target;
    if (el.getAttribute && el.getAttribute("fx-push-url") != null) {
      e.detail.cfg.__irisPush = el.getAttribute("fx-action");
    }
  });
  document.addEventListener("fx:swapped", (e) => {
    const url = e.detail.cfg.__irisPush;
    if (url) history.pushState({ irisUrl: url }, "", url);
  });
  window.addEventListener("popstate", () => {
    // Re-request the current URL into the app shell's main region, if present.
    const target = document.querySelector("[data-iris-main]");
    if (!target) return;
    fetch(location.href, { headers: { "FX-Request": "true" } })
      .then((r) => r.text())
      .then((html) => { target.innerHTML = html; })
      .catch(() => {});
  });

  // --- Polling -----------------------------------------------------------
  const duration = (s) => {
    const m = /^(\d+(?:\.\d+)?)(ms|s|m)?$/.exec((s || "").trim());
    if (!m) return 0;
    const n = parseFloat(m[1]);
    return m[2] === "s" ? n * 1000 : m[2] === "m" ? n * 60000 : n;
  };
  const setupPolling = (root) => {
    const els = root && root.querySelectorAll ? root.querySelectorAll("[fx-poll]") : [];
    els.forEach((el) => {
      if (el.__irisPoll) return;
      const ms = duration(el.getAttribute("fx-poll"));
      if (!ms) return;
      el.__irisPoll = setInterval(() => {
        if (!document.contains(el)) { clearInterval(el.__irisPoll); return; }
        if (el.__fixi) el.__fixi(new CustomEvent("fx:poll"));
      }, ms);
    });
  };
  document.addEventListener("DOMContentLoaded", () => setupPolling(document));
  document.addEventListener("fx:swapped", () => setupPolling(document));
})();
