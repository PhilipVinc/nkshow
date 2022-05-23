from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache, partial
from os import scandir
import os
import os.path

from rich.console import RenderableType
import rich.repr
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.console import Group
from rich.align import Align

from pathlib import Path

from textual import events, log
from textual.message import Message
from textual.reactive import Reactive
from textual._types import MessageTarget
from textual.widgets import TreeControl, TreeClick, TreeNode, NodeID
from textual.widgets import Button, ButtonPressed

from ..database import data as database
from ..filewatching import DirWatcher, observer

from watchdog import events


@dataclass
class DirEntry:
    path: str

    @property
    def is_dir(self):
        return True


@dataclass
class FileEntry:
    path: str
    disabled: bool = False

    @property
    def is_dir(self):
        return False

    @property
    def type(self):
        if self.path.endswith((".log", ".json")):
            return 0
        elif self.path.endswith((".py", ".toml")):
            return 1
        else:
            return 2


@dataclass
class JsonEntry:
    path: str
    file: str
    is_dir: bool


@rich.repr.auto
class FileClick(Message, bubble=True):
    def __init__(self, sender: MessageTarget, path: str) -> None:
        self.path = path
        super().__init__(sender)


@rich.repr.auto
class JsonClick(Message, bubble=True):
    def __init__(self, sender: MessageTarget, file: str, path: str) -> None:
        self.file = file
        self.path = path
        super().__init__(sender)


@rich.repr.auto
class FixPlot(Message, bubble=True):
    def __init__(self, sender: MessageTarget, file: str, path: str, fix: bool) -> None:
        self.file = file
        self.path = path
        self.fix = fix
        super().__init__(sender)


def file_type(entry):
    if entry.is_dir():
        return 1
    elif entry.name.endswith(".log") or entry.name.endswith(".json"):
        return 0
    else:
        return 2


class DirectoryTree(TreeControl[DirEntry]):
    def __init__(self, path: str, name: str = None) -> None:
        self.path = path.rstrip("/")
        label = os.path.basename(self.path)
        if os.path.isdir(path):
            data = DirEntry(path)
        else:
            data = FileEntry(path)
        super().__init__(label, name=name, data=data)
        self.root.tree.guide_style = "black"

        self._watchers = {}
        self._to_refresh = []

        self._status = {}

    has_focus: Reactive[bool] = Reactive(False)

    def on_focus(self) -> None:
        self.has_focus = True

    def on_blur(self) -> None:
        self.has_focus = False

    async def watch_hover_node(self, hover_node: NodeID) -> None:
        for node in self.nodes.values():
            node.tree.guide_style = (
                "bold not dim red" if node.id == hover_node else "black"
            )
        log(f"refresh from hover")
        self.refresh(layout=True)

    def render_node(self, node: TreeNode[DirEntry]) -> RenderableType:
        # log(f"rendering {node}:{node.data} -> {node.expanded}//{node.children}")
        label = self.render_tree_label(
            node,
            node.data.is_dir,
            node.expanded,
            node.is_cursor,
            node.id == self.hover_node,
            self.has_focus,
            self._status.get(node.id, False),
        )
        return label

    @lru_cache(maxsize=1024 * 32)
    def render_tree_label(
        self,
        node: TreeNode[DirEntry],
        is_dir: bool,
        expanded: bool,
        is_cursor: bool,
        is_hover: bool,
        has_focus: bool,
        highlight: bool,
    ) -> RenderableType:
        meta = {
            "@click": f"click_label({node.id})",
            "tree_node": node.id,
            "cursor": node.is_cursor,
        }
        meta_btn = {
            "@click": f"click_btn({node.id})",
            "tree_node": node.id,
            "cursor": node.is_cursor,
        }
        label = Text(node.label) if isinstance(node.label, str) else node.label
        button = None

        if is_hover:
            label.stylize("underline")
        if is_dir:
            label.stylize("bold magenta")
            icon = "📂" if expanded else "📁"
        else:
            label.stylize("bright_green")
            label.highlight_regex(r"\..*$", "green")
            if isinstance(node.data, JsonEntry):
                icon = "📊"
                if highlight:
                    button = Text("-", style="red encircle")
                else:
                    button = Text("+", style="encircle")

                button.apply_meta(meta_btn)
            elif isinstance(node.data, FileEntry):
                typ = node.data.type
                if typ == 0:
                    icon = "💾"
                elif typ == 1:
                    icon = "📝"
                else:
                    icon = "📄"

        if label.plain.startswith("."):
            label.stylize("dim")

        if isinstance(node, DirEntry) and not is_dir:
            if not (label.plain.endswith(".log") or label.plain.endswith(".json")):
                label.stylize("dim")

        if is_cursor and has_focus:
            label.stylize("reverse")

        icon_label = Text(f"{icon} ", no_wrap=True, overflow="ellipsis") + label
        icon_label.apply_meta(meta)

        if button is None:
            return icon_label
        else:
            table = Table(show_header=False, show_lines=False, show_edge=False)
            table.add_row(icon_label, Align(button, "left"))

            return table

    async def on_mount(self, event: events.Mount) -> None:
        log(f"OnMount: loading directory {self.root}")
        await self.load_obj(self.root)
        self.set_interval(5, self.process_events)
        self.refresh(layout=True)

    async def load_directory(self, node: TreeNode[DirEntry]):
        log(f"Loading directory {node.data.path}")
        path = node.data.path
        directory = sorted(
            list(scandir(path)), key=lambda entry: (file_type(entry), entry.name)
        )
        for entry in directory:
            log(f"Loading entry {entry}")
            if entry.is_dir():
                await node.add(entry.name, DirEntry(entry.path))
            else:
                await node.add(entry.name, FileEntry(entry.path))

        if node not in self._watchers:
            handler = DirWatcher(lambda ev: self.refresh_dir(node, ev))
            self._watchers[node] = observer.schedule(handler, path, recursive=False)

        node.loaded = True
        await node.expand()
        self.refresh(layout=True)
        log(f"FINISHED directory {node.data.path} for {node}")

    async def load_json(self, node: TreeNode[DirEntry]):
        log(f"Loading file {node.data.path}")
        path = node.data.path
        if isinstance(node.data, FileEntry):
            file = path
            path = None
        else:
            file = node.data.file

        data = database.get_data(file, path)

        if hasattr(data, "keys"):
            ks = list(data.keys())
        else:
            ks = list(range(len(data)))

        ks = sorted(ks, key=lambda entry: (not isinstance(data[entry], dict), entry))
        for k in ks:
            full_path = f"{k}" if path is None else f"{path}/{k}"
            await node.add(k, JsonEntry(full_path, file, isinstance(data[k], dict)))

        node.loaded = True
        self.refresh(layout=True)
        log(f"FINISHED file {node.data.path}")

    def load_obj(self, node):
        if isinstance(node.data, JsonEntry):
            return self.load_json(node)
        elif isinstance(node.data, FileEntry):
            if database.load_file(node.data.path):
                return self.load_json(node)
            else:
                return self.load_text_file(node)
        else:
            return self.load_directory(node)

    def refresh_dir(self, path, event):
        self._to_refresh.append((path, event))

    async def process_events(self) -> None:
        while len(self._to_refresh) > 0:
            node, event = self._to_refresh.pop()
            log(f"processing event {node} : {event}")
            if isinstance(event, events.FileMovedEvent):
                pass
            elif isinstance(event, events.FileCreatedEvent):
                full_path = event.src_path
                if os.path.isdir(full_path):
                    await node.add(Path(full_path).name, DirEntry(full_path))
                else:
                    await node.add(Path(full_path).name, FileEntry(full_path))

    async def handle_tree_click(self, message: TreeClick[DirEntry]) -> None:
        dir_entry = message.node.data
        log(f"processsing click on {dir_entry}")

        if isinstance(dir_entry, JsonEntry) and not dir_entry.is_dir:
            log(f" -> sending CLICK {dir_entry}")
            await self.emit(JsonClick(self, dir_entry.file, dir_entry.path))
        elif isinstance(dir_entry, FileEntry):
            if database.load_file(message.node.data.path):
                if not message.node.loaded:
                    await self.load_obj(message.node)
                    await message.node.expand()
                else:
                    await message.node.toggle()
            else:
                await self.emit(FileClick(self, dir_entry.path))
        else:
            if not message.node.loaded:
                await self.load_obj(message.node)
                await message.node.expand()
            else:
                await message.node.toggle()

    async def action_click_btn(self, node_id: NodeID) -> None:
        log(f" -> sending CLICKBTN {node_id}")
        node = self.nodes[node_id]
        self._status[node_id] = not self._status.get(node_id, False)
        await self.post_message(
            FixPlot(self, node.data.file, node.data.path, self._status[node_id])
        )

    async def clear_activated(self):
        for k in self._status.keys():
            self._status[k] = False
        self.refresh()


if __name__ == "__main__":
    from textual import events
    from textual.app import App

    class TreeApp(App):
        async def on_mount(self, event: events.Mount) -> None:
            await self.view.dock(DirectoryTree("."))

    TreeApp.run(log="textual.slog")
