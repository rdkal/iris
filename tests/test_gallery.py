"""Tests for the static gallery build."""

from __future__ import annotations

from iris.gallery import build, render_gallery


def test_render_gallery_contains_components_and_chrome():
    html = render_gallery()
    assert html.lower().startswith("<!doctype html>")
    # chrome
    assert 'id="theme-toggle"' in html
    assert "panel-card" in html and "data-copy" in html
    assert "navigator.clipboard" in html
    # a representative spread of components, each with an anchor section
    for name in ["Button", "Card", "Banner", "Table"]:
        assert f'id="{name}"' in html
        assert f'href="#{name}"' in html


def test_inline_style_not_escaped():
    html = render_gallery()
    # the light-theme attribute selector must survive verbatim in <style>
    assert '[data-theme="light"]' in html


def test_inline_script_not_escaped():
    html = render_gallery()
    script = html.split("<script>")[1].split("</script>")[0]
    assert "navigator.clipboard.writeText" in script
    assert "=== 'light'" in script  # JS string literal intact


def test_example_source_appears_in_code_block():
    html = render_gallery()
    # source text without quotes survives as-is; the panel head names component+title
    assert "Row(gap=2)" in html  # from Button's "Variants" example source
    assert "Button · Variants" in html


def test_build_writes_index(tmp_path):
    out = build(tmp_path / "site")
    assert out.name == "index.html"
    assert out.exists()
    assert "panel-card" in out.read_text(encoding="utf-8")
