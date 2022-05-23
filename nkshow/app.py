import os
import sys
from rich.console import RenderableType

from rich.syntax import Syntax
from rich.traceback import Traceback
from rich.panel import Panel
from rich.table import Table

from textual.app import App
from textual.widgets import Header, Footer, FileClick, ScrollView, Static
from textual.views import WindowView
from textual import log

from .widgets import (
    DirectoryTree,
    PlotextMixin,
    JsonClick,
    FileClick,
    TableView,
    PlotPanel,
    PlotController,
)
from .database import data as database


class MyApp(App):
    """An example of a very simple Textual App"""

    async def on_load(self) -> None:
        """Sent before going in to application mode."""

        # Bind our basic keys
        await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")
        await self.bind("c", "clear_plot()", "Clear Plot Panels")
        await self.bind("q", "quit", "Quit")

        # Get path to show
        try:
            self.path = sys.argv[1]
        except IndexError:
            self.path = "."

    async def on_mount(self) -> None:
        """Call after terminal goes in to application mode"""

        # Create our widgets
        # In this a scroll view for the code and a directory tree
        self.directory = DirectoryTree(self.path)
        # self.plot_controller = PlotController()
        self.plotview = PlotPanel(name="Plot panel")
        self.inspector = TableView()

        await self.view.dock(Header(), edge="top")
        grid = await self.view.dock_grid(edge="left", name="left")
        await self.view.dock(Footer(), edge="bottom")
        grid.add_column(name="left", size=48)
        grid.add_column(name="right", max_size=2000)

        grid.add_row(name="top")
        grid.add_row(name="bottom")

        grid.add_areas(
            area1="left,top-start|bottom-end",
            # area2="left,bottom",
            area3="right,top",
            area4="right,bottom",
        )

        grid.place(
            area1=ScrollView(self.directory),
            # area2=self.plot_controller,
            area3=self.plotview,
            area4=self.inspector,
        )

        self._selected = []
        self._data = None

    async def handle_json_click(self, message: JsonClick) -> None:
        """A message sent by the directory tree when a file is clicked."""

        log(f"GOT message {message}")
        await self.inspector.show_data(message.file, message.path)
        log(f" ->  updated inspector with {message}")
        await self.plotview.set_plot_data(
            message.file, message.path, "iters", "Mean", clear=False
        )
        # await self.plot_controller.show_data(message.file, message.path)
        log(f" ->  updated plot with {message}")
        self.app.sub_title = os.path.basename(message.path)

    async def handle_file_click(self, message: FileClick) -> None:
        """A message sent by the directory tree when a file is clicked."""

        log(f"GOT message (shw file) {message}")
        await self.inspector.show_file(message.path)
        log(f" ->  updated inspector with sbowfke {message}")
        self.app.sub_title = os.path.basename(message.path)

    async def handle_fix_plot(self, message) -> None:
        """A message sent by the directory tree when a file is clicked."""
        log(f"GOT message (fix_plot) {message}")
        if message.fix:
            await self.plotview.fix_plot_data(
                message.file, message.path, "iters", "Mean", clear=False
            )
        else:
            await self.plotview.unfix_plot_data(
                message.file, message.path, "iters", "Mean"
            )

    async def action_clear_plot(self) -> None:
        log(f"GOT ACTION clear plot")
        await self.directory.clear_activated()
        await self.plotview.clear_plot()
