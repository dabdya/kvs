import json
import os


class StorageInitError(Exception):
    def __init__(self, text=""):
        self.text = text


class Storage:
    def __init__(self, path):
        self._path = path
        self._data = None

    def init(self):
        head, tail = os.path.split(self._path)
        if not tail:
            text = "Storage name not specified"
            raise StorageInitError(text)

        try:
            os.makedirs(head)
        except (FileNotFoundError, FileExistsError):
            pass

        if os.path.exists(self._path):
            text = f"Storage '{tail}' already exists"
            raise StorageInitError(text)

        with open(self._path, "w") as storage:
            storage.write(json.dumps(dict()))

    def __len__(self):
        return len(self._data)

    def __enter__(self):
        with open(self._path, "r") as storage:
            try:
                self._data = json.load(storage)
                if not isinstance(self._data, dict):
                    raise TypeError("Unsupported storage data format")
            except json.JSONDecodeError:
                raise TypeError("Unsupported storage file format")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self._path, "w") as storage:
            storage.write(json.dumps(self._data))

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getitem__(self, key):
        return self._data[key]

    def __delitem__(self, key):
        del self._data[key]

    def __contains__(self, item):
        return item in self._data

    def __iter__(self):
        return iter(self._data)
