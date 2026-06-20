// iris-test.js — in-browser test harness for the "stub" testing mode.
// The page embeds two application/json script tags, id="iris-routes" (a map of
// URL -> pre-rendered fragment HTML) and id="iris-steps" (the list of steps).
// This script intercepts fixi requests (fx:config) and serves the matching
// pre-rendered fragment from a canned Response, runs the steps, and reports the
// result in-page (a banner + window.__iris_test = {done, passed, failures}).
(() => {
  const read = (id) => {
    const el = document.getElementById(id);
    try { return el ? JSON.parse(el.textContent) : null; } catch (e) { return null; }
  };

  // --- Error collection (installed before fixi runs) ---------------------
  const errors = [];
  window.addEventListener("error", (e) => errors.push("error: " + (e.message || e.error)));
  window.addEventListener("unhandledrejection", (e) => errors.push("unhandledrejection: " + e.reason));
  const realConsoleError = console.error.bind(console);
  console.error = (...args) => { errors.push("console.error: " + args.join(" ")); realConsoleError(...args); };
  document.addEventListener("fx:error", (e) => errors.push("fx:error: " + (e.detail && e.detail.error)));

  // --- Stub interception: serve embedded fragments via cfg.fetch ---------
  const routes = read("iris-routes") || {};
  document.addEventListener("fx:config", (e) => {
    const cfg = e.detail.cfg;
    const path = cfg.action;
    if (Object.prototype.hasOwnProperty.call(routes, path)) {
      const body = routes[path];
      cfg.fetch = () => Promise.resolve(new Response(body, { status: 200, headers: { "Content-Type": "text/html" } }));
    } else {
      cfg.fetch = () => Promise.resolve(new Response("no stub route: " + path, { status: 404 }));
    }
  });

  // --- Steps engine ------------------------------------------------------
  const steps = read("iris-steps") || [];
  const failures = [];
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  async function run() {
    try {
      for (const step of steps) {
        if (step.click != null) {
          const el = document.querySelector(step.click);
          if (!el) { failures.push("click: no element " + step.click); continue; }
          el.click();
          await sleep(step.wait != null ? step.wait : 60);
        } else if (step.fill != null) {
          const el = document.querySelector(step.fill);
          if (!el) { failures.push("fill: no element " + step.fill); continue; }
          el.value = step.value != null ? step.value : "";
        } else if (step.expect_text != null) {
          if (!document.body.innerText.includes(step.expect_text))
            failures.push("expect_text missing: " + JSON.stringify(step.expect_text));
        } else if (step.expect_absent != null) {
          if (document.body.innerText.includes(step.expect_absent))
            failures.push("expect_absent found: " + JSON.stringify(step.expect_absent));
        } else if (step.wait != null) {
          await sleep(step.wait);
        }
      }
    } catch (err) {
      failures.push("exception: " + err);
    }
    for (const e of errors) failures.push(e);
    report();
  }

  function report() {
    const passed = failures.length === 0;
    window.__iris_test = { done: true, passed, failures };
    const banner = document.createElement("div");
    banner.id = "iris-test-result";
    banner.setAttribute("data-passed", String(passed));
    // Normal flow at the top of the page so it never overlaps the content.
    banner.style.cssText =
      "padding:.5rem 1rem;font:600 13px system-ui;color:#fff;" +
      "background:" + (passed ? "#2e7d32" : "#c62828");
    banner.textContent = passed ? "✓ iris test passed" : "✗ iris test failed: " + failures.join(" | ");
    document.body.insertBefore(banner, document.body.firstChild);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run);
  else run();
})();
