from watchdog.events import FileSystemEventHandler

from textual import log


class FileWatcher(FileSystemEventHandler):
    """Logs all the events captured."""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_modified(self, event):
        super().on_modified(event)
        # log(f"processing event moved {event}")
        self.callback(event)
