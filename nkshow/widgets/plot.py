from rich.layout import Layout
from rich.live import Live
from rich.ansi import AnsiDecoder
from rich.console import Group
from rich.jupyter import JupyterMixin
from rich.panel import Panel
from rich.text import Text

from textual import log

from time import sleep
import plotext as plt

import numpy as np


class PlotextMixin(JupyterMixin):
    def __init__(self, phase=0, title=""):
        self.decoder = AnsiDecoder()
        self.phase = phase
        self.title = title
        self.data = []

    def __rich_console__(self, console, options):
        self.width = options.max_width or console.width
        self.height = options.height or console.height
        log(f"plotting with {self.width} and {self.height}")
        canvas = self.make_plot(self.width, self.height, self.phase, self.title)
        self.rich_canvas = Group(*self.decoder.decode(canvas))
        yield self.rich_canvas

    def make_plot(self, width, height, phase=0, title=""):
        plt.clf()
        for (xdata, ydata, label) in self.data:
            plt.plot(xdata.real, ydata.real, label=label)
        plt.plotsize(width, height)
        plt.title(title)
        plt.theme("dark")
        if hasattr(self, "ylim") and self.ylim is not None:
            plt.ylim(*self.ylim)
        # plt.cls()
        return plt.build()
