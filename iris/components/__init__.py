"""iris components, grouped by family (see DESIGN.md §3)."""

from __future__ import annotations

from .data import Avatar, Badge, Empty, List, Stat, Table, Tag
from .feedback import Banner, Progress, Skeleton, Spinner
from .forms import Button
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
]
