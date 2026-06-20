"""Tests for data-display and feedback components."""

from __future__ import annotations

from iris import (
    Avatar,
    Badge,
    Banner,
    Button,
    Empty,
    List,
    Progress,
    Skeleton,
    Spinner,
    Stat,
    Table,
    Tag,
    render,
)


def test_button_default_type_and_variant():
    out = render(Button(".primary")["Save"])
    assert out == '<button class="btn primary" type="button">Save</button>'


def test_badge_and_tag():
    assert 'class="badge accent"' in render(Badge(".accent")["3"])
    assert render(Tag["py"]) == '<span class="tag">py</span>'


def test_avatar_initials_vs_image():
    assert render(Avatar["AB"]) == '<span class="avatar">AB</span>'
    img = render(Avatar(src="/a.png", alt="Ada"))
    assert img.startswith("<img") and 'class="avatar"' in img and 'src="/a.png"' in img


def test_stat_value_and_label():
    out = render(Stat(label="Users", value="1,204"))
    assert 'class="stat-value">1,204</div>' in out
    assert 'class="stat-label">Users</div>' in out


def test_empty_state():
    out = render(Empty(title="Nothing", icon="x")["body"])
    assert 'class="empty"' in out and "Nothing" in out and "body" in out


def test_list_from_items():
    out = render(List(items=["a", "b"]))
    assert out == '<ul class="list"><li>a</li><li>b</li></ul>'


def test_list_from_children():
    from iris import h

    assert render(List[h.li["x"]]) == '<ul class="list"><li>x</li></ul>'


def test_table_headers_and_rows():
    out = render(Table(headers=["Name"], rows=[["Ada"], ["Linus"]]))
    assert "<thead><tr><th>Name</th></tr></thead>" in out
    assert "<tbody><tr><td>Ada</td></tr><tr><td>Linus</td></tr></tbody>" in out


def test_spinner_has_status_role():
    out = render(Spinner())
    assert 'role="status"' in out and 'class="spinner"' in out


def test_skeleton_dimensions():
    out = render(Skeleton(width="60%", height="1rem"))
    assert "width:60%" in out and "height:1rem" in out


def test_banner_variant_and_role():
    out = render(Banner(".error", role="alert")["boom"])
    assert 'class="banner error"' in out and 'role="alert"' in out


def test_progress_value():
    out = render(Progress(value=66))
    assert out == '<progress class="progress" max="100" value="66"></progress>'
