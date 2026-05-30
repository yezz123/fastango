"""Brand colors and Rich style helpers for Fastango."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

DARK = "#141413"
LIGHT = "#faf9f5"
MID_GRAY = "#b0aea5"
LIGHT_GRAY = "#e8e6dc"
ORANGE = "#d97757"
BLUE = "#6a9bcc"
GREEN = "#788c5d"

FASTANGO_THEME = Theme(
    {
        "fastango.title": f"bold {ORANGE}",
        "fastango.subtitle": BLUE,
        "fastango.success": GREEN,
        "fastango.muted": MID_GRAY,
        "fastango.error": "bold red",
        "fastango.accent": ORANGE,
    }
)


def make_console() -> Console:
    return Console(theme=FASTANGO_THEME)


def brand_panel(message: str, *, title: str = "Fastango") -> Panel:
    text = Text(message, style="fastango.subtitle")
    return Panel(text, title=f"[fastango.title]{title}[/]", border_style=ORANGE)
