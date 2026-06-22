"""Charts — a tiny grammar-of-graphics ``Plot``. See DESIGN.md §9.

Server-rendered SVG, no JS, themed by the tokens. A plot is a set of **marks**
(``Dot`` for now) bound to data via **channels** (``x``, ``y``, ``color``),
composed in the plot's ``[...]`` slot::

    Plot(width=640, height=400)[
        Dot(people, x="weight", y="height", color="sex"),
    ]

A legend is shown automatically when a ``color`` channel is present; pass
``legend=True``/``False`` to force it on or off.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterable

from ..core import classes, component
from ..html import h

__all__ = ["Plot", "Dot", "Mark", "PALETTE"]

# Categorical palette (distinct hues that read well on the dark theme).
PALETTE = [
    "#6ea8fe", "#22d3aa", "#f0883e", "#f1707a",
    "#c08cff", "#facc15", "#4dd0e1", "#a3e635",
]


@dataclass
class Mark:
    """A plot layer: data plus the channels mapping fields to position/colour."""

    kind: str
    data: list[dict[str, Any]]
    x: str
    y: str
    color: str | None = None
    r: float = 4.0


def Dot(data: Iterable[dict[str, Any]], *, x: str, y: str,
        color: str | None = None, r: float = 4.0) -> Mark:
    """The point mark (Observable's ``dot``). ``data`` is a list of records."""

    return Mark("dot", list(data), x=x, y=y, color=color, r=r)


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
    """SVG coordinate as a string (htpy only accepts str/int attribute values)."""

    value = round(value, 2)
    return str(int(value)) if value == int(value) else str(value)


def _fmt(value: float) -> str:
    return str(int(value)) if value == int(value) else f"{value:g}"


def _nice_ticks(lo: float, hi: float, count: int = 5) -> list[float]:
    """~``count`` evenly spaced 'nice' tick values spanning [lo, hi]."""

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


@component
def Plot(children: Any = None, *, width: float = 640, height: float = 400,
         legend: bool | None = None, x_label: str | None = None,
         y_label: str | None = None, **attrs: Any) -> Any:
    marks = _flatten(children)
    xs = [row[m.x] for m in marks for row in m.data]
    ys = [row[m.y] for m in marks for row in m.data]
    cls = classes("plot", attrs.pop("class_", None))
    if not xs or not ys:
        return h.figure(class_=cls, **attrs)[
            h.svg(class_="plot-svg", width=_n(width), height=_n(height),
                  viewBox=f"0 0 {_n(width)} {_n(height)}")
        ]

    # ordered distinct colour categories across marks
    categories: list[Any] = []
    for m in marks:
        if m.color:
            for row in m.data:
                cat = row.get(m.color)
                if cat not in categories:
                    categories.append(cat)
    color_for = {cat: PALETTE[i % len(PALETTE)] for i, cat in enumerate(categories)}

    pad_l, pad_r, pad_t, pad_b = 52, 16, 16, 44
    x_ticks = _nice_ticks(min(xs), max(xs))
    y_ticks = _nice_ticks(min(ys), max(ys))
    x0, x1 = min(min(xs), x_ticks[0]), max(max(xs), x_ticks[-1])
    y0, y1 = min(min(ys), y_ticks[0]), max(max(ys), y_ticks[-1])
    px0, px1 = pad_l, width - pad_r
    py0, py1 = height - pad_b, pad_t  # bottom -> top (inverted)

    def sx(v: float) -> float:
        return px0 + (v - x0) / (x1 - x0) * (px1 - px0)

    def sy(v: float) -> float:
        return py0 + (v - y0) / (y1 - y0) * (py1 - py0)

    mid_x, mid_y = (px0 + px1) / 2, (py0 + py1) / 2
    grid = [
        *(h.line(class_="plot-grid", x1=_n(sx(t)), x2=_n(sx(t)),
                 y1=_n(py1), y2=_n(py0)) for t in x_ticks),
        *(h.line(class_="plot-grid", x1=_n(px0), x2=_n(px1),
                 y1=_n(sy(t)), y2=_n(sy(t))) for t in y_ticks),
    ]
    axis = [
        *(h.text(class_="plot-tick", x=_n(sx(t)), y=_n(py0 + 16),
                 text_anchor="middle")[_fmt(t)] for t in x_ticks),
        *(h.text(class_="plot-tick", x=_n(px0 - 8), y=_n(sy(t) + 4),
                 text_anchor="end")[_fmt(t)] for t in y_ticks),
    ]
    labels = [
        h.text(class_="plot-label", x=_n(mid_x), y=_n(height - 6),
               text_anchor="middle")[x_label or marks[0].x],
        h.text(class_="plot-label", x="14", y=_n(mid_y), text_anchor="middle",
               transform=f"rotate(-90 14 {_n(mid_y)})")[y_label or marks[0].y],
    ]
    points = []
    for m in marks:
        for row in m.data:
            cx, cy = _n(sx(row[m.x])), _n(sy(row[m.y]))
            if m.color:
                points.append(h.circle(cx=cx, cy=cy, r=_n(m.r),
                                        style=f"fill:{color_for[row.get(m.color)]}"))
            else:
                points.append(h.circle(".plot-dot", cx=cx, cy=cy, r=_n(m.r)))

    svg = h.svg(class_="plot-svg", width=_n(width), height=_n(height),
                viewBox=f"0 0 {_n(width)} {_n(height)}", role="img")[
        h.g(class_="plot-grid-g")[grid],
        h.g(class_="plot-axis")[axis],
        labels,
        h.g(class_="plot-points")[points],
    ]

    show_legend = bool(categories) if legend is None else (legend and bool(categories))
    legend_node = h.div(".plot-legend")[
        (
            h.span(".plot-legend-item")[
                h.span(".plot-swatch", style=f"background:{color_for[cat]}"),
                str(cat),
            ]
            for cat in categories
        )
    ] if show_legend else None

    return h.figure(class_=cls, **attrs)[legend_node, svg]


# --- Examples ------------------------------------------------------------ #

_SAMPLE = [
    {"weight": 52, "height": 158, "sex": "f"}, {"weight": 61, "height": 165, "sex": "f"},
    {"weight": 68, "height": 170, "sex": "f"}, {"weight": 55, "height": 161, "sex": "f"},
    {"weight": 78, "height": 179, "sex": "m"}, {"weight": 85, "height": 183, "sex": "m"},
    {"weight": 72, "height": 174, "sex": "m"}, {"weight": 90, "height": 188, "sex": "m"},
]


@Plot.example("Scatter with color")
def _():
    return Plot(width=520, height=320)[
        Dot(_SAMPLE, x="weight", y="height", color="sex"),
    ]


@Plot.example("Single series (no legend)")
def _():
    return Plot(width=520, height=320)[
        Dot(_SAMPLE, x="weight", y="height"),
    ]
