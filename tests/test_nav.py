"""Tests for navigation components."""

from __future__ import annotations

from iris import AppShell, Breadcrumbs, Header, NavLink, Page, Tab, Tabs, render


def test_navlink_emits_fixi_and_real_href():
    out = render(NavLink(href="/search")["Search"])
    assert 'href="/search"' in out
    assert 'fx-action="/search"' in out
    assert 'fx-target="[data-iris-main]"' in out
    assert "fx-push-url" in out


def test_navlink_push_can_be_disabled():
    assert "fx-push-url" not in render(NavLink(href="/x", push=False)["x"])


def test_tabs_marks_active():
    out = render(Tabs(active="Home", tabs=[Tab("Home", "/home"), Tab("Search", "/search")]))
    assert 'class="tab active"' in out
    assert 'aria-current="page"' in out
    assert out.count('class="tab"') == 1  # only the inactive one


def test_tab_icon_rendered():
    out = render(Tabs(tabs=[Tab("Home", "/home", icon="H")]))
    assert 'class="tab-icon"' in out and ">H<" in out


def test_appshell_structure():
    out = render(AppShell(title="iris", active="Home", tabs=[Tab("Home", "/home")])["body"])
    assert 'class="appshell"' in out
    assert "data-iris-main" in out
    assert 'class="header"' in out
    assert 'class="tabs"' in out
    assert "body" in out


def test_breadcrumbs():
    out = render(Breadcrumbs(items=[("Home", "/"), ("Lib", "/lib"), "Now"]))
    assert out.count("crumb-sep") == 2
    assert 'href="/lib"' in out
    assert "crumb-current" in out and "Now" in out


def test_page_fixi_inlines_scripts():
    out = render(Page(fixi=True)["x"])
    assert "__fixi_mo" in out  # fixi.js
    assert "__iris_fixi" in out  # iris-fixi.js


def test_page_without_fixi_has_no_js():
    assert "__fixi_mo" not in render(Page["x"])
