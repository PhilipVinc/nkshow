from __future__ import annotations

from rich import box
from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.pretty import Pretty
import rich.repr
from rich.traceback import Traceback

from logging import getLogger

from textual import events, log
from textual.geometry import Offset
from textual.widget import Reactive, Widget

import numpy as np

from .plot import PlotextMixin
from ..database import data as database


@rich.repr.auto(angular=False)
class PlotPanel(Widget, can_focus=True):

    has_focus: Reactive[bool] = Reactive(False)
    mouse_over: Reactive[bool] = Reactive(False)
    style: Reactive[str] = Reactive("")

    def __init__(self, *, name: str) -> None:
        super().__init__(name=name)

        self._plot = PlotextMixin()

        self.renderable = self._plot

        self._plot_keys_fixed = []
        self._plot_keys_last = []

    def __rich_repr__(self) -> rich.repr.Result:
        yield "name", self.name

    def render(self) -> RenderableType:
        return Panel(
            self.renderable,
            title=self.__class__.__name__,
            border_style="green" if self.mouse_over else "blue",
            box=box.HEAVY if self.has_focus else box.ROUNDED,
            style=self.style,
        )

    async def on_focus(self, event: events.Focus) -> None:
        self.has_focus = True

    async def on_blur(self, event: events.Blur) -> None:
        self.has_focus = False

    async def on_enter(self, event: events.Enter) -> None:
        self.mouse_over = True

    async def on_leave(self, event: events.Leave) -> None:
        self.mouse_over = False

    async def fix_plot_data(self, file, path, xlabel, ylabel, clear=False):
        if clear:
            self._plot_keys_fixed = []
        self._plot_keys_fixed.append((file, path, (xlabel, ylabel)))
        await self.update_plot()

    async def unfix_plot_data(self, file, path, xlabel, ylabel):
        self._plot_keys_fixed.remove((file, path, (xlabel, ylabel)))
        await self.update_plot()

    async def set_plot_data(self, file, path, xlabel, ylabel, clear=False):
        if clear:
            self._plot_keys = []
        self._plot_keys_last = (file, path, (xlabel, ylabel))
        await self.update_plot()

    async def update_plot(self):
        log(f"Updating plots with {self._plot_keys_fixed}")
        try:
            data = []
            if self._plot_keys_last in self._plot_keys_fixed:
                plot_keys = self._plot_keys_fixed
            else:
                plot_keys = self._plot_keys_fixed + [self._plot_keys_last]
            for (file, path, (xlabel, ylabel)) in plot_keys:

                hist = database.get_data(file, path)
                log("PlotPanel: Loaded {file} {path}")
                data.append((hist[xlabel], hist[ylabel], f"{file}/{path}/{ylabel}"))

            self._plot.data = data
            content = self._plot

        except Exception:
            # Possibly a binary file
            # For demonstration purposes we will show the traceback
            content = Traceback(theme="monokai", width=None, show_locals=True)

        self.renderable = content
        self.refresh()

    async def clear_plot(self):
        self._plot_keys_fixed = []
        await self.update_plot()
