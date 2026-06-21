"""Tests for overlay components, icons, and (browser) native popover behavior."""

from __future__ import annotations

import pytest

from iris import Drawer, Icon, Menu, Modal, Page, Popover, Toast, h, render


def test_modal_wires_trigger_to_popover():
    out = render(Modal(trigger="Open", title="Title", id="m1")["body"])
    assert 'popovertarget="m1"' in out
    assert 'id="m1"' in out and 'popover="auto"' in out
    assert 'popovertargetaction="hide"' in out  # close button
    assert "Title" in out and "body" in out


def test_drawer_side_class():
    out = render(Drawer(trigger="Open", side="left", id="d1")["x"])
    assert "drawer drawer-left" in out
    assert 'popovertarget="d1"' in out


def test_menu_and_popover_anchor():
    assert "anchor-name:--menu1" in render(Menu(trigger="m", id="menu1")["i"])
    assert "position-anchor:--pop1" in render(Popover(trigger="p", id="pop1")["c"])


def test_toast_variant():
    assert 'class="toast success"' in render(Toast(".success")["Saved"])


def test_icon_renders_svg_with_currentcolor():
    out = render(Icon(name="home"))
    assert "<svg" in out and 'stroke="currentColor"' in out and 'viewBox="0 0 24 24"' in out


def test_icon_unknown_name_raises():
    with pytest.raises(KeyError):
        render(Icon(name="nope"))


def test_icon_composes_in_slots():
    from iris import Tab, Tabs

    out = render(Tabs(tabs=[Tab("Home", "/home", icon=Icon(name="home"))]))
    assert "<svg" in out and 'class="tab-icon"' in out


# --- Browser: native popover open/close (no JS) -------------------------- #

pytest.importorskip("playwright.sync_api")


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            pw.chromium.launch().close()
        return True
    except Exception:
        return False


browser = pytest.mark.skipif(not _chromium_available(), reason="Chromium not installed")


@browser
def test_modal_opens_and_closes_natively():
    from playwright.sync_api import sync_playwright

    html = render(
        Page(title="t")[
            Modal(trigger="Open modal", title="Hi", id="m1")[h.p["Modal body here"]]
        ]
    )
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        try:
            page = b.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.set_content(html, wait_until="load")
            opened = '#m1'
            assert not page.locator(opened).evaluate('el => el.matches(":popover-open")')
            page.click('button[popovertarget="m1"]')
            page.wait_for_selector("#m1:popover-open")
            assert page.locator("text=Modal body here").is_visible()
            page.click(".overlay-close")
            page.wait_for_timeout(150)
            assert not page.locator(opened).evaluate('el => el.matches(":popover-open")')
            assert errors == []
        finally:
            b.close()
