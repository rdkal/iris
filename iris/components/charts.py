"""Charts — a tiny grammar-of-graphics ``Plot`` and a ``Graph`` built on it.

See DESIGN.md §9. Server-rendered SVG, no JS (interactivity is opt-in via
``iris-plot.js``), themed by the tokens.

A plot is a set of **marks** bound to data via **channels**, composed in the
plot's ``[...]`` slot::

    Plot()[ Dot(people, x="weight", y="height", color="sex") ]

Networks are Plot-unified: ``Graph(nodes, edges, layout=...)`` runs a layout,
resolves edges to coordinates, and returns a ``Plot`` of ``Link`` + ``Node``
marks.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from secrets import token_hex
from typing import Any, Iterable

from ..assets import iris_plot_js
from ..core import classes, component, raw
from ..html import h

__all__ = ["Plot", "Dot", "Node", "Link", "Graph", "Mark", "PALETTE"]

PALETTE = [
    "#6ea8fe", "#22d3aa", "#f0883e", "#f1707a",
    "#c08cff", "#facc15", "#4dd0e1", "#a3e635",
]


@dataclass
class Mark:
    """A plot layer. ``kind`` selects how its channels are interpreted."""

    kind: str
    data: list[dict[str, Any]]
    # point channels (dot / node)
    x: str | None = None
    y: str | None = None
    color: str | None = None
    fill: str | None = None
    label: Any = None
    size: str | float | None = None
    r: float = 4.0
    # link channels
    x1: str | None = None
    y1: str | None = None
    x2: str | None = None
    y2: str | None = None
    width: str | float | None = None
    directed: bool = False


def Dot(data: Iterable[dict[str, Any]], *, x: str, y: str, color: str | None = None,
        fill: str | None = None, label: Any = None, r: float = 4.0) -> Mark:
    """The point mark. ``color`` is a field (palette + legend); ``fill`` is a
    constant colour for the whole layer (give it a ``label`` to legend it)."""

    return Mark("dot", list(data), x=x, y=y, color=color, fill=fill, label=label, r=r)


def Node(data: Iterable[dict[str, Any]], *, x: str = "x", y: str = "y",
         color: str | None = None, fill: str | None = None, label: str | None = None,
         size: str | float | None = None, r: float = 6.0) -> Mark:
    """The node mark — ``Dot`` plus ``size`` (field or constant px) and ``label``
    (field) channels."""

    return Mark("node", list(data), x=x, y=y, color=color, fill=fill,
                label=label, size=size, r=r)


def Link(data: Iterable[dict[str, Any]], *, x1: str = "x1", y1: str = "y1",
         x2: str = "x2", y2: str = "y2", color: str | None = None,
         fill: str | None = None, width: str | float | None = None,
         directed: bool = False) -> Mark:
    """The segment mark connecting (x1,y1)->(x2,y2). ``directed`` adds an
    arrowhead."""

    return Mark("link", list(data), x1=x1, y1=y1, x2=x2, y2=y2, color=color,
                fill=fill, width=width, directed=directed)


def _flatten(children: Any) -> list[Mark]:
    if children is None:
        return []
    if isinstance(children, Mark):
        return [children]
    out: list[Mark] = []
    for child in children:
        out.extend(_flatten(child))
    return out


def _n(value: float) -> str:
    value = round(value, 2)
    return str(int(value)) if value == int(value) else str(value)


def _fmt(value: float) -> str:
    return str(int(value)) if value == int(value) else f"{value:g}"


def _nice_ticks(lo: float, hi: float, count: int = 5) -> list[float]:
    if lo == hi:
        hi = lo + 1
    raw_step = (hi - lo) / count
    mag = 10 ** math.floor(math.log10(raw_step))
    norm = raw_step / mag
    step = (1 if norm < 1.5 else 2 if norm < 3 else 5 if norm < 7 else 10) * mag
    start = math.floor(lo / step) * step
    ticks: list[float] = []
    v = start
    while v <= hi + step * 1e-9:
        if v >= lo - step * 1e-9:
            ticks.append(round(v, 10))
        v += step
    return ticks or [lo, hi]


def _mark_coords(m: Mark) -> tuple[list[float], list[float]]:
    if m.kind == "link":
        xs = [r[m.x1] for r in m.data] + [r[m.x2] for r in m.data]
        ys = [r[m.y1] for r in m.data] + [r[m.y2] for r in m.data]
    else:
        xs = [r[m.x] for r in m.data]
        ys = [r[m.y] for r in m.data]
    return xs, ys


@component
def Plot(children: Any = None, *, width: float = 640, height: float = 400,
         legend: bool | None = None, x_label: str | None = None,
         y_label: str | None = None, axes: bool = True, interactive: bool = False,
         **attrs: Any) -> Any:
    marks = _flatten(children)
    cls = classes("plot", attrs.pop("class_", None))
    xs: list[float] = []
    ys: list[float] = []
    for m in marks:
        mx, my = _mark_coords(m)
        xs += mx
        ys += my
    if not xs or not ys:
        return h.figure(class_=cls, **attrs)[
            h.svg(class_="plot-svg", width=_n(width), height=_n(height),
                  viewBox=f"0 0 {_n(width)} {_n(height)}")
        ]

    # colour categories across all marks that map a colour field
    categories: list[Any] = []
    for m in marks:
        if m.color:
            for row in m.data:
                cat = row.get(m.color)
                if cat not in categories:
                    categories.append(cat)
    color_for = {cat: PALETTE[i % len(PALETTE)] for i, cat in enumerate(categories)}

    # size scale (node marks with a size *field*)
    size_vals = [row[m.size] for m in marks
                 if m.kind == "node" and isinstance(m.size, str) for row in m.data]
    s_lo, s_hi = (min(size_vals), max(size_vals)) if size_vals else (0.0, 1.0)

    def radius(m: Mark, row: dict[str, Any]) -> float:
        if m.size is None:
            return m.r
        if isinstance(m.size, (int, float)):
            return float(m.size)
        v = row[m.size]
        return 4.0 if s_hi == s_lo else 4.0 + (v - s_lo) / (s_hi - s_lo) * 12.0

    # width scale (link marks with a width *field*)
    w_vals = [row[m.width] for m in marks
              if m.kind == "link" and isinstance(m.width, str) for row in m.data]
    w_lo, w_hi = (min(w_vals), max(w_vals)) if w_vals else (0.0, 1.0)

    def stroke_w(m: Mark, row: dict[str, Any]) -> float:
        if m.width is None:
            return 1.0
        if isinstance(m.width, (int, float)):
            return float(m.width)
        v = row[m.width]
        return 1.5 if w_hi == w_lo else 1.0 + (v - w_lo) / (w_hi - w_lo) * 5.0

    x_ticks = _nice_ticks(min(xs), max(xs))
    y_ticks = _nice_ticks(min(ys), max(ys))
    if axes:
        pad_l, pad_r, pad_t, pad_b = 52, 16, 16, 44
        x0, x1 = min(min(xs), x_ticks[0]), max(max(xs), x_ticks[-1])
        y0, y1 = min(min(ys), y_ticks[0]), max(max(ys), y_ticks[-1])
        px0, px1, py0, py1 = pad_l, width - pad_r, height - pad_b, pad_t

        def sx(v: float) -> float:
            return px0 + (v - x0) / (x1 - x0) * (px1 - px0)

        def sy(v: float) -> float:
            return py0 + (v - y0) / (y1 - y0) * (py1 - py0)
    else:
        # graph mode: equal aspect, centred, no axes
        pad = 14
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        dx, dy = (x1 - x0) or 1, (y1 - y0) or 1
        aw, ah = width - 2 * pad, height - 2 * pad
        s = min(aw / dx, ah / dy)
        ox = pad + (aw - s * dx) / 2
        oy = pad + (ah - s * dy) / 2

        def sx(v: float) -> float:
            return ox + (v - x0) * s

        def sy(v: float) -> float:
            return oy + (y1 - v) * s

    arrow_id = f"plot-arrow-{token_hex(3)}"
    any_directed = any(m.kind == "link" and m.directed for m in marks)

    link_nodes: list[Any] = []
    for m in (mk for mk in marks if mk.kind == "link"):
        for row in m.data:
            opts: dict[str, Any] = dict(
                x1=_n(sx(row[m.x1])), y1=_n(sy(row[m.y1])),
                x2=_n(sx(row[m.x2])), y2=_n(sy(row[m.y2])),
                stroke_width=_n(stroke_w(m, row)),
            )
            stroke = color_for[row[m.color]] if m.color else m.fill
            if stroke:
                opts["style"] = f"stroke:{stroke}"
            if m.directed:
                opts["marker_end"] = f"url(#{arrow_id})"
            link_nodes.append(h.line(class_="plot-link", **opts))

    point_nodes: list[Any] = []
    for m in (mk for mk in marks if mk.kind in ("dot", "node")):
        for row in m.data:
            cx, cy = sx(row[m.x]), sy(row[m.y])
            rad = radius(m, row)
            fill = color_for[row[m.color]] if m.color else m.fill
            if fill:
                point_nodes.append(h.circle(cx=_n(cx), cy=_n(cy), r=_n(rad),
                                             style=f"fill:{fill}"))
            else:
                point_nodes.append(h.circle(".plot-dot", cx=_n(cx), cy=_n(cy), r=_n(rad)))
            if m.kind == "node" and m.label:
                point_nodes.append(
                    h.text(class_="plot-node-label", x=_n(cx + rad + 3), y=_n(cy + 3))[
                        str(row.get(m.label, ""))
                    ]
                )

    body: list[Any] = []
    if axes:
        body.append(h.g(class_="plot-grid-g")[
            *(h.line(class_="plot-grid", x1=_n(sx(t)), x2=_n(sx(t)),
                     y1=_n(py1), y2=_n(py0)) for t in x_ticks),
            *(h.line(class_="plot-grid", x1=_n(px0), x2=_n(px1),
                     y1=_n(sy(t)), y2=_n(sy(t))) for t in y_ticks),
        ])
        mid_x, mid_y = (px0 + px1) / 2, (py0 + py1) / 2
        body.append(h.g(class_="plot-axis")[
            *(h.text(class_="plot-tick", x=_n(sx(t)), y=_n(py0 + 16),
                     text_anchor="middle")[_fmt(t)] for t in x_ticks),
            *(h.text(class_="plot-tick", x=_n(px0 - 8), y=_n(sy(t) + 4),
                     text_anchor="end")[_fmt(t)] for t in y_ticks),
        ])
        body.append(h.text(class_="plot-label", x=_n(mid_x), y=_n(height - 6),
                           text_anchor="middle")[x_label or marks[0].x])
        body.append(h.text(class_="plot-label", x="14", y=_n(mid_y),
                           text_anchor="middle",
                           transform=f"rotate(-90 14 {_n(mid_y)})")[y_label or marks[0].y])
    body.append(h.g(class_="plot-links")[link_nodes])
    body.append(h.g(class_="plot-points")[point_nodes])

    content: list[Any] = []
    if any_directed:
        content.append(h.svg(role="presentation")[
            raw(
                f'<defs><marker id="{arrow_id}" viewBox="0 0 10 10" refX="9" refY="5" '
                'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                '<path class="plot-arrow" d="M0 0 L10 5 L0 10 z" /></marker></defs>'
            )
        ])
    content.append(h.g(class_="plot-zoom")[body] if interactive else h.g[body])

    svg = h.svg(class_=classes("plot-svg", "plot-interactive" if interactive else None),
                width=_n(width), height=_n(height),
                viewBox=f"0 0 {_n(width)} {_n(height)}", role="img")[content]

    # legend: colour categories + constant-fill layers that carry a label
    # (a node mark's `label` is a per-node text field, not a legend entry).
    legend_entries: list[tuple[str, str]] = [(str(c), color_for[c]) for c in categories]
    for m in marks:
        if m.kind != "node" and m.label is not None and not m.color:
            legend_entries.append((str(m.label), m.fill or "var(--accent)"))

    show = bool(legend_entries) if legend is None else (legend and bool(legend_entries))
    legend_node = h.div(".plot-legend")[
        (h.span(".plot-legend-item")[h.span(".plot-swatch", style=f"background:{c}"), lab]
         for lab, c in legend_entries)
    ] if show else None

    return h.figure(class_=cls, **attrs)[
        legend_node, svg,
        h.script[iris_plot_js()] if interactive else None,
    ]


# --- Layouts ------------------------------------------------------------- #

def _circular(ids: list[Any]) -> dict[Any, tuple[float, float]]:
    n = len(ids) or 1
    return {i: (math.cos(2 * math.pi * k / n), math.sin(2 * math.pi * k / n))
            for k, i in enumerate(ids)}


def _grid(ids: list[Any]) -> dict[Any, tuple[float, float]]:
    cols = max(1, math.ceil(len(ids) ** 0.5))
    return {i: (k % cols, -(k // cols)) for k, i in enumerate(ids)}


def _force(ids: list[Any], edges: list[tuple[Any, Any]], *, seed: int = 1,
           iterations: int = 200) -> dict[Any, tuple[float, float]]:
    rnd = random.Random(seed)
    pos = {i: [rnd.uniform(0, 1), rnd.uniform(0, 1)] for i in ids}
    n = len(ids) or 1
    k = (1.0 / n) ** 0.5
    t = 0.1
    for _ in range(iterations):
        disp = {i: [0.0, 0.0] for i in ids}
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                i, j = ids[a], ids[b]
                dx, dy = pos[i][0] - pos[j][0], pos[i][1] - pos[j][1]
                d = (dx * dx + dy * dy) ** 0.5 or 1e-6
                f = k * k / d
                ux, uy = dx / d, dy / d
                disp[i][0] += ux * f; disp[i][1] += uy * f
                disp[j][0] -= ux * f; disp[j][1] -= uy * f
        for u, v in edges:
            dx, dy = pos[u][0] - pos[v][0], pos[u][1] - pos[v][1]
            d = (dx * dx + dy * dy) ** 0.5 or 1e-6
            f = d * d / k
            ux, uy = dx / d, dy / d
            disp[u][0] -= ux * f; disp[u][1] -= uy * f
            disp[v][0] += ux * f; disp[v][1] += uy * f
        for i in ids:
            dx, dy = disp[i]
            d = (dx * dx + dy * dy) ** 0.5 or 1e-6
            pos[i][0] += dx / d * min(d, t)
            pos[i][1] += dy / d * min(d, t)
        t *= 0.95
    return {i: (pos[i][0], pos[i][1]) for i in ids}


def Graph(nodes: Iterable[dict[str, Any]], edges: Iterable[dict[str, Any]], *,
          layout: str = "force", id: str = "id", source: str = "source",
          target: str = "target", node_color: str | None = None,
          node_size: str | float | None = None, node_label: str | None = None,
          node_fill: str | None = None, edge_color: str | None = None,
          edge_width: str | float | None = None, directed: bool = False,
          width: float = 640, height: float = 480, interactive: bool = False,
          legend: bool | None = None, **attrs: Any) -> Any:
    """A node-link network diagram — a convenience wrapper that lays the graph
    out and returns a :func:`Plot` of ``Link`` + ``Node`` marks (see DESIGN §9).

    ``layout`` is ``"force"`` | ``"circular"`` | ``"grid"`` | ``"precomputed"``
    (the last reads ``x``/``y`` off each node). ``node_size="degree"`` sizes nodes
    by their degree.
    """

    nodes = list(nodes)
    edges = list(edges)
    ids = [nd[id] for nd in nodes]

    if node_size == "degree":
        deg = {i: 0 for i in ids}
        for e in edges:
            for end in (e.get(source), e.get(target)):
                if end in deg:
                    deg[end] += 1
        nodes = [{**nd, "degree": deg[nd[id]]} for nd in nodes]

    if layout in ("precomputed", "none"):
        pos = {nd[id]: (nd["x"], nd["y"]) for nd in nodes}
    elif layout == "circular":
        pos = _circular(ids)
    elif layout == "grid":
        pos = _grid(ids)
    else:
        idset = set(ids)
        eidx = [(e[source], e[target]) for e in edges
                if e.get(source) in idset and e.get(target) in idset]
        pos = _force(ids, eidx)

    positioned = [{**nd, "_x": pos[nd[id]][0], "_y": pos[nd[id]][1]} for nd in nodes]
    segments = []
    for e in edges:
        a, b = pos.get(e.get(source)), pos.get(e.get(target))
        if a and b:
            segments.append({**e, "_x1": a[0], "_y1": a[1], "_x2": b[0], "_y2": b[1]})

    return Plot(width=width, height=height, axes=False, interactive=interactive,
                legend=legend, **attrs)[
        Link(segments, x1="_x1", y1="_y1", x2="_x2", y2="_y2",
             color=edge_color, width=edge_width, directed=directed),
        Node(positioned, x="_x", y="_y", color=node_color, fill=node_fill,
             size=node_size, label=node_label),
    ]


# --- Examples (hand-formatted narrow for the docs; ruff leaves them be) -- #


@Plot.example("Scatter with color")
def _():
    # fmt: off
    people = [
        {"kg": 52, "cm": 158, "sex": "f"},
        {"kg": 61, "cm": 165, "sex": "f"},
        {"kg": 68, "cm": 170, "sex": "f"},
        {"kg": 78, "cm": 179, "sex": "m"},
        {"kg": 85, "cm": 183, "sex": "m"},
        {"kg": 90, "cm": 188, "sex": "m"},
    ]
    return Plot(width=420, height=300)[
        Dot(
            people,
            x="kg",
            y="cm",
            color="sex",
        ),
    ]
    # fmt: on


@Plot.example("Pick colors (two series)")
def _():
    # fmt: off
    a = [
        {"x": 1, "y": 2},
        {"x": 2, "y": 4},
        {"x": 3, "y": 3},
    ]
    b = [
        {"x": 1, "y": 5},
        {"x": 2, "y": 3},
        {"x": 3, "y": 6},
    ]
    return Plot(width=420, height=300)[
        Dot(a, x="x", y="y",
            fill="#6ea8fe", label="A"),
        Dot(b, x="x", y="y",
            fill="#22d3aa", label="B"),
    ]
    # fmt: on


@Plot.example("Graph (force layout)")
def _():
    # fmt: off
    nodes = [
        {"id": "a", "team": "x"},
        {"id": "b", "team": "x"},
        {"id": "c", "team": "x"},
        {"id": "d", "team": "y"},
        {"id": "e", "team": "y"},
    ]
    edges = [
        {"source": "a", "target": "b"},
        {"source": "a", "target": "c"},
        {"source": "b", "target": "c"},
        {"source": "c", "target": "d"},
        {"source": "d", "target": "e"},
    ]
    return Graph(
        nodes, edges,
        layout="force",
        node_color="team",
        node_size="degree",
        node_label="id",
        width=420, height=320,
    )
    # fmt: on


@Plot.example("Graph (circular, directed)")
def _():
    # fmt: off
    nodes = [{"id": n} for n in "abcde"]
    edges = [
        {"source": "a", "target": "b"},
        {"source": "b", "target": "c"},
        {"source": "c", "target": "d"},
        {"source": "d", "target": "e"},
        {"source": "e", "target": "a"},
    ]
    return Graph(
        nodes, edges,
        layout="circular",
        directed=True,
        node_label="id",
        width=360, height=320,
    )
    # fmt: on
