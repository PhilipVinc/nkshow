from watchdog.events import FileSystemEventHandler

from textual import log


class DirWatcher(FileSystemEventHandler):
    """Logs all the events captured."""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_moved(self, event):
        super().on_moved(event)
        # log(f"processing event moved {event}")
        self.callback(event)

    def on_created(self, event):
        super().on_created(event)
        # log(f"processing event creeated {event}")
        self.callback(event)

    def on_deleted(self, event):
        super().on_deleted(event)
        # log(f"processing event deeleted {event}")
        self.callback(event)

    def on_modified(self, event):
        super().on_deleted(event)
        # log(f"processing event deeleted {event}")
        self.callback(event)
