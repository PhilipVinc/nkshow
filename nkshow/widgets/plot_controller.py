from __future__ import annotations

from rich.console import RenderableType
from rich.padding import Padding, PaddingDimensions
from rich.style import StyleType
from rich.styled import Styled

import rich
from rich.text import Text
from rich.syntax import Syntax
from rich.traceback import Traceback
from rich.panel import Panel
from rich.table import Table
from rich.align import Align

from textual import log
from textual.message import Message
from textual.widgets import (
    Header,
    Footer,
    FileClick,
    ScrollView,
    Static,
    Button,
    ButtonPressed,
)

from ..database import data as database


def make_button(
    ctrl, file, path, name: str, showing: bool, style: str = "white on rgb(255,159,7)"
) -> Button:
    """Create a button with the given label."""
    if showing:
        text = "-"
    else:
        text = "+"

    meta = {
        "@click": f"click_btn('{file}', '{path}', '{name}')",
    }

    btn = Text(text)
    btn.apply_meta(meta)
    return btn


@rich.repr.auto
class BtnClick(Message, bubble=True):
    def __init__(self, sender: MessageTarget, path: str) -> None:
        self.path = path
        super().__init__(sender)


class PlotController(ScrollView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buttons_top = {}
        self._datasets = []

    async def show_data(self, file, path) -> None:
        """A message sent by the directory tree when a file is clicked."""

        log(f"PlotController: GOT message {file} {path}")
        try:
            hist = database.get_data(file, path)

            ks = hist.keys()
            showing = {k: (file, path, k) in self._datasets for k in ks}
            self._buttons_top = {
                k: make_button(self, file, path, k, showing[k]) for k in ks
            }

            table = Table()
            for k in ks:
                table.add_row(self._buttons_top[k], Text(k))

            content = Panel(table, title=path)
            log(f"all good in plot panel {content}")

        except Exception:
            # Possibly a binary file
            # For demonstration purposes we will show the traceback
            content = Traceback(theme="monokai", width=None, show_locals=True)
            log(f"got exception in plot panel {content}")
        await self.update(content)

    def handle_button_pressed(self, message: ButtonPressed) -> None:
        """A message sent by the button widget"""

        assert isinstance(message.sender, Button)
        button_name = message.sender.name

        log(f"Pressed button {button_name} : {message}")

    async def action_click_btn(self, file, path, key: NodeID) -> None:
        log(f"PlotController: GOT ACTION CLICK BTN {file}:{path}:{key}")

        await self.post_message(BtnClick(self, key))
