"""Tests for layout/surface components and the theme stylesheet."""

from __future__ import annotations

from iris import (
    Card,
    Center,
    Container,
    Divider,
    Grid,
    LIGHT,
    Page,
    Panel,
    Row,
    Sheet,
    Spacer,
    Stack,
    Theme,
    h,
    render,
    stylesheet,
)


def test_stack_sets_gap_variable():
    out = render(Stack(gap=3)["x"])
    assert 'class="stack"' in out and "--gap: 3" in out


def test_stack_without_gap_has_no_style():
    assert render(Stack["x"]) == '<div class="stack">x</div>'


def test_grid_sets_cols_and_gap():
    out = render(Grid(cols=2, gap=1)["x"])
    assert 'class="grid"' in out
    assert "--cols: 2" in out and "--gap: 1" in out


def test_row_container_center():
    assert 'class="row"' in render(Row["x"])
    assert 'class="container"' in render(Container["x"])
    assert 'class="center"' in render(Center["x"])


def test_divider_is_void_hr():
    assert render(Divider) == '<hr class="divider">'


def test_spacer():
    assert render(Spacer) == '<div class="spacer"></div>'


def test_surfaces():
    assert 'class="card"' in render(Card["x"])
    assert 'class="sheet"' in render(Sheet["x"])
    assert 'class="panel"' in render(Panel["x"])


def test_extra_class_merges_on_surface():
    assert render(Card(".elevated")["x"]) == '<div class="card elevated">x</div>'


def test_page_is_full_document():
    out = render(Page(title="Today")[h.p["hi"]])
    assert out.lower().startswith("<!doctype html>")
    assert '<meta name="viewport"' in out
    assert "<title>Today</title>" in out
    assert "<style>" in out and "--accent" in out
    assert "<p>hi</p>" in out


def test_page_body_attrs():
    out = render(Page(data_app="x")["hi"])
    assert 'data-app="x"' in out


def test_stylesheet_has_root_and_light_and_base():
    css = stylesheet()
    assert ":root" in css
    assert '[data-theme="light"]' in css
    assert ".stack" in css and ".card" in css


def test_stylesheet_light_can_be_omitted():
    css = stylesheet(light=None)
    assert '[data-theme="light"]' not in css


def test_theme_override():
    css = Theme(accent="#22d3aa").root_css()
    assert "--accent: #22d3aa" in css


def test_light_theme_differs():
    assert LIGHT.bg != Theme().bg
