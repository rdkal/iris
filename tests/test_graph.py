"""Tests for the Graph network (grammar-of-graphics layers over Plot)."""

from __future__ import annotations

import re

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


def test_graph_default_layers_draw_nodes_and_edges():
    out = render(Graph(NODES, EDGES, width=400, height=300))
    assert '<figure class="plot"' in out
    assert out.count("<circle") == len(NODES)
    assert out.count("<line") == len(EDGES)
    assert "plot-grid" not in out  # graph mode = no axes


def test_channels_live_on_the_mark_layers():
    out = render(Graph(NODES, EDGES)[
        Link(directed=True),
        Node(color="team", size="degree", label="id"),
    ])
    assert out.count("plot-swatch") == 2          # two teams (legend)
    assert "plot-node-label" in out and ">a<" in out
    assert "marker-end" in out and "plot-arrow" in out


def test_degree_field_is_injected_for_sizing():
    out = render(Graph(NODES, EDGES)[Node(size="degree")])
    radii = set(re.findall(r'<circle[^>]*\br="([^"]+)"', out))
    assert len(radii) >= 2                         # degree varies -> radii vary


def test_extra_mark_is_forwarded_to_plot():
    out = render(Graph(NODES, EDGES)[
        Link(), Node(),
        Dot([{"x": 0.0, "y": 0.0}], x="x", y="y", fill="#facc15"),
    ])
    assert out.count("<circle") == len(NODES) + 1  # forwarded dot too
    assert "fill:#facc15" in out


def test_link_layer_custom_edge_keys():
    nodes = [{"id": 1}, {"id": 2}]
    edges = [{"from": 1, "to": 2}]
    out = render(Graph(nodes, edges)[Link(source="from", target="to"), Node()])
    assert out.count("<line") == 1


@pytest.mark.parametrize("layout", ["force", "circular", "grid"])
def test_layouts_render(layout):
    out = render(Graph(NODES, EDGES, layout=layout))
    assert out.count("<circle") == len(NODES)


def test_precomputed_layout_uses_node_xy():
    nodes = [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 1, "y": 1}]
    out = render(Graph(nodes, [{"source": "a", "target": "b"}], layout="precomputed"))
    assert out.count("<circle") == 2 and out.count("<line") == 1


def test_force_layout_is_deterministic():
    a = render(Graph(NODES, EDGES, layout="force")[Node()])
    b = render(Graph(NODES, EDGES, layout="force")[Node()])
    assert a == b


def test_low_level_node_and_link_marks_on_plot():
    out = render(Plot(axes=False)[
        Link([{"x1": 0, "y1": 0, "x2": 1, "y2": 1}]),
        Node([{"x": 0, "y": 0}, {"x": 1, "y": 1}]),
    ])
    assert out.count("<line") == 1 and out.count("<circle") == 2


def test_interactive_inlines_script_and_zoom_group():
    out = render(Graph(NODES, EDGES, interactive=True)[Node()])
    assert "plot-interactive" in out and 'class="plot-zoom"' in out
    assert "__iris_plot" in out


# --- Browser: pan/zoom actually works ------------------------------------ #

pytest.importorskip("playwright.sync_api")


def test_interactive_pan_zoom(iris_page, iris_errors):
    from iris import Container, Page

    html = render(Page(title="g")[Container[
        Graph(NODES, EDGES, interactive=True, width=400, height=320)[
            Link(), Node(label="id")
        ]
    ]])
    iris_page.set_content(html, wait_until="load")
    box = iris_page.locator("svg.plot-interactive").bounding_box()
    iris_page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    iris_page.mouse.wheel(0, -200)
    iris_page.wait_for_timeout(80)
    transform = iris_page.locator(".plot-zoom").get_attribute("transform")
    assert transform and "scale" in transform
    iris_errors.assert_none()
