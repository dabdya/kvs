import os
import struct

from rbtree import Tree


class StorageInitError(Exception):
    def __init__(self, text=""):
        self.text = text


class Storage:
    def __init__(self, path):
        self._path = path
        self._tree = None

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

        with open(self._path, "wb") as storage:
            pass

        with open(self._path, "rb+") as storage:
            # Количество вершин
            storage.write(struct.pack(">i", 0))
            # Позиция корня
            storage.write(struct.pack(">i", -1))

    def __len__(self):
        pass

    def __enter__(self):
        self._tree = Tree(self._path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __setitem__(self, key, value):
        self._tree.insert(key, value)

    def __getitem__(self, key):
        result = self._tree.find(key)
        if result:
            return result.key

    def __delitem__(self, key):
        pass

    def __contains__(self, item):
        pass

    def __iter__(self):
        pass
