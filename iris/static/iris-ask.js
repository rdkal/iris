// iris-ask.js — show validation errors from a FastAPI/Pydantic response.
//
// No server-side error rendering: the POST handler just validates with Pydantic
// (FastAPI returns its default 422 JSON, {detail:[{loc,msg,...}]}). This hooks
// fixi's fx:after, and when the response is a non-OK JSON body, maps each error
// to the input named by the last element of `loc` — adding `.invalid` to the
// enclosing `.field` and filling its `.field-error` — then cancels the swap.
(() => {
  if (window.__iris_ask) return;
  window.__iris_ask = true;

  document.addEventListener("fx:after", (e) => {
    const cfg = e.detail.cfg;
    const resp = cfg.response;
    if (!resp || resp.ok) return; // success swaps normally
    const ct = resp.headers.get("content-type") || "";
    if (!ct.includes("json")) return;

    let data;
    try { data = JSON.parse(cfg.text); } catch (err) { return; }
    const detail = data && data.detail;
    if (!Array.isArray(detail)) return;

    const scope = (e.target.closest && e.target.closest("form")) || e.target.form || document;

    // clear previous errors in scope
    scope.querySelectorAll(".field.invalid").forEach((f) => f.classList.remove("invalid"));
    scope.querySelectorAll(".field-error").forEach((el) => { el.textContent = ""; });

    detail.forEach((err) => {
      const loc = err.loc || [];
      const name = loc[loc.length - 1];
      if (name == null) return;
      const input = scope.querySelector('[name="' + name + '"]');
      if (!input) return;
      const field = (input.closest && input.closest(".field")) || input.parentElement;
      if (field) field.classList.add("invalid");
      const slot = field && field.querySelector(".field-error");
      if (slot) slot.textContent = err.msg || "Invalid value";
    });

    e.preventDefault(); // we handled the error — don't swap the JSON body in
  });
})();
