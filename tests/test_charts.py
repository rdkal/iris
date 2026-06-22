"""Tests for the Plot / Dot charts."""

from __future__ import annotations

import pytest

from iris import Dot, Plot, render

DATA = [
    {"x": 1, "y": 2, "g": "a"},
    {"x": 3, "y": 5, "g": "b"},
    {"x": 2, "y": 4, "g": "a"},
]


def test_plot_renders_svg_with_a_point_per_row():
    out = render(Plot(width=400, height=300)[Dot(DATA, x="x", y="y")])
    assert '<figure class="plot"' in out
    assert 'viewBox="0 0 400 300"' in out
    assert out.count("<circle") == len(DATA)


def test_legend_shows_by_default_when_color():
    out = render(Plot()[Dot(DATA, x="x", y="y", color="g")])
    assert "plot-legend" in out
    assert out.count("plot-swatch") == 2          # two categories: a, b
    assert ">a<" in out and ">b<" in out
    # categorical colours from the palette
    assert "fill:#6ea8fe" in out and "fill:#22d3aa" in out


def test_no_legend_without_color():
    out = render(Plot()[Dot(DATA, x="x", y="y")])
    assert "plot-legend" not in out
    assert 'class="plot-dot"' in out               # single-series uses the accent class


def test_legend_can_be_forced_off():
    out = render(Plot(legend=False)[Dot(DATA, x="x", y="y", color="g")])
    assert "plot-legend" not in out


def test_axis_labels_default_to_field_names():
    rows = [{"weightz": 1, "heightz": 2}, {"weightz": 3, "heightz": 4}]
    out = render(Plot()[Dot(rows, x="weightz", y="heightz")])
    assert ">weightz<" in out and ">heightz<" in out


def test_custom_axis_labels():
    out = render(Plot(x_label="Weight (kg)", y_label="Height (cm)")[Dot(DATA, x="x", y="y")])
    assert "Weight (kg)" in out and "Height (cm)" in out


def test_multiple_marks_share_scales():
    out = render(Plot()[
        Dot(DATA, x="x", y="y", color="g"),
        Dot([{"x": 5, "y": 1, "g": "c"}], x="x", y="y", color="g"),
    ])
    assert out.count("<circle") == 4
    assert out.count("plot-swatch") == 3           # a, b, c


def test_empty_plot_is_safe():
    out = render(Plot())
    assert '<figure class="plot"' in out and "<svg" in out


# --- Browser smoke: a plot page has no JS/render errors ------------------ #

pytest.importorskip("playwright.sync_api")


def test_plot_renders_in_browser(iris_page, iris_errors):
    from iris import Container, Page

    html = render(Page(title="chart")[Container[Plot()[Dot(DATA, x="x", y="y", color="g")]]])
    iris_page.set_content(html, wait_until="load")
    assert iris_page.locator("circle").count() == 3
    iris_errors.assert_none()
