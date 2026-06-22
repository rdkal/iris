"""iris — a small, server-side UI toolkit for Python, built on htpy.

See DESIGN.md for the full design. Quick start::

    from iris import Page, Stack, Grid, Card, h

    Page(title="Today")[
        Stack(gap=3)[
            Grid(cols=2)[
                Card[ h.h3["Eggs"],  h.p["with spam"] ],
                Card[ h.h3["Bacon"], h.p["with eggs"] ],
            ],
        ]
    ]
"""

from __future__ import annotations

from .components import (
    AppShell,
    Avatar,
    Badge,
    Banner,
    Breadcrumbs,
    Button,
    Card,
    Center,
    Checkbox,
    Container,
    Divider,
    Dot,
    Drawer,
    Empty,
    Field,
    Form,
    Grid,
    Header,
    Icon,
    Input,
    List,
    Menu,
    Modal,
    NavLink,
    Page,
    Panel,
    Plot,
    Popover,
    Progress,
    Row,
    Select,
    Sheet,
    Skeleton,
    Spacer,
    Spinner,
    Stack,
    Stat,
    Switch,
    Tab,
    Table,
    Tabs,
    Tag,
    Textarea,
    Toast,
)
from .core import (
    Example,
    classes,
    component,
    is_fx,
    raw,
    registered_components,
    render,
    render_stream,
    root,
)
from .html import h
from .theme import DARK, LIGHT, Theme, stylesheet

__version__ = "0.1.0"

__all__ = [
    "__version__",
    # core
    "component",
    "render",
    "render_stream",
    "is_fx",
    "classes",
    "root",
    "raw",
    "Example",
    "registered_components",
    "h",
    # theme
    "Theme",
    "DARK",
    "LIGHT",
    "stylesheet",
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
    # overlay
    "Modal",
    "Drawer",
    "Menu",
    "Popover",
    "Toast",
    # icons
    "Icon",
    # charts
    "Plot",
    "Dot",
]
