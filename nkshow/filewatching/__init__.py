from .dir_watcher import DirWatcher
from .file_watch import FileWatcher

from watchdog.observers import Observer as _Observer

observer = _Observer()
observer.start()
