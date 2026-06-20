# iris

A small, server-side UI toolkit for Python, built on [htpy](https://htpy.dev).

You build pages by **composing components** — plain function calls that nest just
like htpy, but hand you ready-made UI pieces (`Page`, `Card`, `Grid`, `Stack`, …)
that are dark, minimal, and mobile-first by default.

```python
from iris import Page, Stack, Grid, Card, h, render

doc = Page(title="Today")[
    Stack(gap=3)[
        h.h1["Menu"],
        Grid(cols=2)[
            Card[ h.h3["Eggs"],  h.p["with spam"] ],
            Card[ h.h3["Bacon"], h.p["with eggs"] ],
        ],
    ]
]

html = render(doc)   # a full, self-contained HTML document
```

- `Comp(...)` sets props — htpy class/id shorthand (`".primary"`, `"#main"`),
  keyword attributes, and `fx_*` attributes for [fixi](https://github.com/bigskysoftware/fixi).
- `Comp[...]` sets children — the same bracket syntax as htpy.
- `h` is htpy itself, so raw tags mix freely with components.

Write your own component — it's just a function:

```python
from iris import component, Card, Row, h

@component
def ArticleCard(children, *, title, body, tags):
    return Card[
        h.h2[title],
        h.p[body],
        Row(gap=1)[(h.span(".tag")[t] for t in tags)],
    ]
```

## Status

Early. See [DESIGN.md](./DESIGN.md) for the full design and [TODO.md](./TODO.md)
for what's built. Implemented so far: the core (`@component`, `render`,
`render_stream`, `is_fx`), the theme tokens + dark stylesheet, and the layout and
surface components.

## Install

```bash
pip install -e .          # core
pip install -e ".[test]"  # + pytest & playwright (browser testing, WIP)
```

## License

MIT
