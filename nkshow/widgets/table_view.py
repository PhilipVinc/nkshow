from __future__ import annotations

from rich.console import RenderableType
from rich.padding import Padding, PaddingDimensions
from rich.style import StyleType
from rich.styled import Styled

from rich.syntax import Syntax
from rich.traceback import Traceback
from rich.panel import Panel
from rich.table import Table
from rich.align import Align

from textual import log
from textual.widgets import Header, Footer, FileClick, ScrollView, Static

from ..database import data as database


class TableView(ScrollView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def show_data(self, file, path) -> None:
        """A message sent by the directory tree when a file is clicked."""

        log(f"GOT message {file} {path}")

        content: RenderableType

        try:
            hist = database.get_data(file, path)
            ks = ["iters"] + hist.keys()

            # Construct a Syntax object for the path in the message
            table = Table(
                *ks,
            )

            datas = [hist[k] for k in ks]
            for i in range(len(hist)):
                table.add_row(*[f"{d[i]}" for d in datas])

            content = Panel(table, title=path)

        except Exception:
            # Possibly a binary file
            # For demonstration purposes we will show the traceback
            content = Traceback(theme="monokai", width=None, show_locals=True)

        panel = Align.center(content)

        await self.update(panel)

    async def show_file(self, path) -> None:
        """A message sent by the directory tree when a file is clicked."""

        log(f"GOT message (show file) {path}")
        syntax: RenderableType
        try:
            # Construct a Syntax object for the path in the message
            syntax = Syntax.from_path(
                path,
                line_numbers=True,
                word_wrap=True,
                indent_guides=True,
                theme="monokai",
            )
        except Exception:
            # Possibly a binary file
            # For demonstration purposes we will show the traceback
            syntax = Traceback(theme="monokai", width=None, show_locals=True)

        await self.update(syntax)
