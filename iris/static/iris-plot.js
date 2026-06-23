// iris-plot.js — opt-in pan + wheel-zoom for an iris Plot/Graph (no deps).
// Enabled by Plot(interactive=True) / Graph(interactive=True), which mark the
// <svg class="plot-interactive"> and wrap the drawing in <g class="plot-zoom">.
(() => {
  if (window.__iris_plot) return;
  window.__iris_plot = true;

  const setup = (svg) => {
    const g = svg.querySelector(".plot-zoom");
    if (!g || svg.__iris_plot) return;
    svg.__iris_plot = true;
    let scale = 1, tx = 0, ty = 0, dragging = false, lx = 0, ly = 0;
    const vw = () => svg.viewBox.baseVal.width || svg.clientWidth;
    const vh = () => svg.viewBox.baseVal.height || svg.clientHeight;
    const apply = () => g.setAttribute("transform", `translate(${tx} ${ty}) scale(${scale})`);

    svg.addEventListener("wheel", (e) => {
      e.preventDefault();
      const r = svg.getBoundingClientRect();
      const mx = ((e.clientX - r.left) / r.width) * vw();
      const my = ((e.clientY - r.top) / r.height) * vh();
      const f = e.deltaY < 0 ? 1.1 : 1 / 1.1;
      tx = mx - (mx - tx) * f;
      ty = my - (my - ty) * f;
      scale *= f;
      apply();
    }, { passive: false });

    svg.addEventListener("pointerdown", (e) => {
      dragging = true; lx = e.clientX; ly = e.clientY;
      svg.setPointerCapture(e.pointerId);
    });
    svg.addEventListener("pointermove", (e) => {
      if (!dragging) return;
      const r = svg.getBoundingClientRect();
      tx += (e.clientX - lx) * (vw() / r.width);
      ty += (e.clientY - ly) * (vh() / r.height);
      lx = e.clientX; ly = e.clientY;
      apply();
    });
    const stop = () => { dragging = false; };
    svg.addEventListener("pointerup", stop);
    svg.addEventListener("pointercancel", stop);
  };

  const init = () => document.querySelectorAll("svg.plot-interactive").forEach(setup);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
