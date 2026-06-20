"""iris components, grouped by family (see DESIGN.md §3)."""

from __future__ import annotations

from .data import Avatar, Badge, Empty, List, Stat, Table, Tag
from .feedback import Banner, Progress, Skeleton, Spinner
from .forms import Button, Checkbox, Field, Form, Input, Select, Switch, Textarea
from .layout import (
    Center,
    Container,
    Divider,
    Grid,
    Page,
    Row,
    Spacer,
    Stack,
)
from .nav import AppShell, Breadcrumbs, Header, NavLink, Tab, Tabs
from .surfaces import Card, Panel, Sheet

__all__ = [
    # layout
    "Page",
    "Container",
    "Stack",
    "Row",
    "Grid",
    "Center",
    "Divider",
    "Spacer",
    # navigation
    "Header",
    "NavLink",
    "Tab",
    "Tabs",
    "AppShell",
    "Breadcrumbs",
    # surfaces
    "Card",
    "Sheet",
    "Panel",
    # data display
    "Badge",
    "Tag",
    "Avatar",
    "Stat",
    "Empty",
    "List",
    "Table",
    # feedback
    "Spinner",
    "Skeleton",
    "Banner",
    "Progress",
    # forms
    "Button",
    "Form",
    "Field",
    "Input",
    "Textarea",
    "Select",
    "Checkbox",
    "Switch",
]
