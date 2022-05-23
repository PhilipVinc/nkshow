from textual import log

from ..filewatching import FileWatcher, DirWatcher, observer

from .loading import loadfile


class Database:
    def __init__(self):
        self._files = {}
        self._text_files = {}

        self._dirty = set()

        self._watchers = {}

    def load_file(self, path):
        log(f"Loading file {path} in Database (dirty={self._dirty})")
        success = True
        try:
            data = loadfile(path)
            self._files[path] = data
        except Exception:
            success = False

        if path in self._dirty:
            log("removing dirty path {path}")
            self._dirty.remove(path)

        if success and path not in self._watchers:
            handler = DirWatcher(lambda ev: self.notify_dirty_file(path))
            self._watchers[path] = observer.schedule(handler, path, recursive=True)
            log(f"Adding file watcher {handler}")

        return success

    def notify_dirty_file(self, path):
        self._dirty.add(path)

    def load_text_file(self, path):
        with open(path, "r"):
            data = path.read()
        return data

    def get_data(self, file_path, dict_path=None):
        log(f"Database: get_data({file_path},{dict_path}) (dirty={self._dirty})")
        if file_path not in self._files:
            raise ValueError("File {file_path} not open!")

        if file_path in self._dirty:
            log(f" -> is dirty")
            self.load_file(file_path)

        data = self._files[file_path]

        if dict_path is None:
            return data

        for k in dict_path.split("/"):
            data = data[k]

        log(f" -> return ({file_path},{dict_path})")

        return data
