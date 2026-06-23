"""Tests for the Graph network wrapper, layouts, and Plot interactivity."""

from __future__ import annotations

import pytest

from iris import Dot, Graph, Link, Node, Plot, render

NODES = [
    {"id": "a", "team": "x"},
    {"id": "b", "team": "x"},
    {"id": "c", "team": "y"},
    {"id": "d", "team": "y"},
]
EDGES = [
    {"source": "a", "target": "b"},
    {"source": "b", "target": "c"},
    {"source": "c", "target": "d"},
]


def test_graph_draws_nodes_and_edges():
    out = render(Graph(NODES, EDGES, width=400, height=300))
    assert '<figure class="plot"' in out
    assert out.count("<circle") == len(NODES)
    assert out.count("<line") == len(EDGES)
    assert "viewBox=" in out and "plot-grid" not in out  # graph mode = no axes


def test_node_color_legend_and_labels():
    out = render(Graph(NODES, EDGES, node_color="team", node_label="id"))
    assert out.count("plot-swatch") == 2          # two teams
    assert "plot-node-label" in out and ">a<" in out


def test_node_size_by_degree():
    # degree differs across nodes -> at least two distinct radii
    out = render(Graph(NODES, EDGES, node_size="degree"))
    import re

    radii = set(re.findall(r'<circle[^>]*\br="([^"]+)"', out))
    assert len(radii) >= 2


def test_directed_adds_arrowheads():
    out = render(Graph(NODES, EDGES, directed=True))
    assert "marker-end" in out and "plot-arrow" in out


@pytest.mark.parametrize("layout", ["force", "circular", "grid"])
def test_layouts_render(layout):
    out = render(Graph(NODES, EDGES, layout=layout))
    assert out.count("<circle") == len(NODES)


def test_precomputed_layout_uses_node_xy():
    nodes = [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 1, "y": 1}]
    out = render(Graph(nodes, [{"source": "a", "target": "b"}], layout="precomputed"))
    assert out.count("<circle") == 2 and out.count("<line") == 1


def test_force_layout_is_deterministic():
    a = render(Graph(NODES, EDGES, layout="force"))
    b = render(Graph(NODES, EDGES, layout="force"))
    assert a == b


def test_low_level_node_and_link_marks_on_plot():
    out = render(Plot(axes=False)[
        Link([{"x1": 0, "y1": 0, "x2": 1, "y2": 1}]),
        Node([{"x": 0, "y": 0}, {"x": 1, "y": 1}]),
    ])
    assert out.count("<line") == 1 and out.count("<circle") == 2


def test_interactive_inlines_script_and_zoom_group():
    out = render(Plot(interactive=True)[Dot([{"x": 1, "y": 2}], x="x", y="y")])
    assert "plot-interactive" in out and 'class="plot-zoom"' in out
    assert "__iris_plot" in out  # iris-plot.js inlined
    assert "plot-interactive" not in render(Plot()[Dot([{"x": 1, "y": 2}], x="x", y="y")])


# --- Browser: pan/zoom actually works ------------------------------------ #

pytest.importorskip("playwright.sync_api")


def test_interactive_pan_zoom(iris_page, iris_errors):
    from iris import Container, Page

    html = render(Page(title="g")[Container[
        Graph(NODES, EDGES, interactive=True, width=400, height=320)
    ]])
    iris_page.set_content(html, wait_until="load")
    box = iris_page.locator("svg.plot-interactive").bounding_box()
    iris_page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    iris_page.mouse.wheel(0, -200)
    iris_page.wait_for_timeout(80)
    transform = iris_page.locator(".plot-zoom").get_attribute("transform")
    assert transform and "scale" in transform
    iris_errors.assert_none()
