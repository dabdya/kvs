from itertools import chain
from enum import Enum
import struct


class NodeColor(Enum):
    Black = 0,
    Red = 1

    @staticmethod
    def to_byte(color):
        color = color == NodeColor.Red
        return struct.pack(">?", color)

    @staticmethod
    def to_bool(color):
        return color == NodeColor.Red

    @staticmethod
    def from_byte(color_byte):
        color = struct.unpack(">?", color_byte)[0]
        return NodeColor.Red if color else NodeColor.Black


class NodeStream:
    storage = r"\\"
    tree_size = 128
    size_row = 25
    len_size = 4
    root_pointer_size = 4

    @classmethod
    def get_node(cls, index):
        if index == -1:
            return None
        with open(cls.storage, "rb") as storage:
            storage.seek(
                index * cls.size_row + NodeStream.len_size
                + NodeStream.root_pointer_size, 0)
            data = storage.read(NodeStream.size_row)
            if len(data) != NodeStream.size_row:
                return None
            index = struct.unpack(">i", data[0:4])[0]
            left = struct.unpack(">i", data[4:8])[0]
            right = struct.unpack(">i", data[8:12])[0]
            parent = struct.unpack(">i", data[12:16])[0]
            color = NodeColor.from_byte(data[16:17])
            key = struct.unpack(">i", data[17:21])[0]
            value = struct.unpack(">i", data[21:25])[0]
            return Node(index, key, value,
                        left=left, right=right,
                        parent=parent, color=color)

    @classmethod
    def nodes_count(cls):
        with open(cls.storage, "rb") as storage:
            data = storage.read(4)
            return struct.unpack(">i", data)[0]

    @classmethod
    def nodes_count_up(cls, last):
        with open(cls.storage, "rb+") as storage:
            storage.write(struct.pack(">i", last + 1))

    @classmethod
    def get_root_index(cls):
        with open(cls.storage, "rb") as storage:
            storage.seek(NodeStream.len_size)
            data = storage.read(4)
            return struct.unpack(">i", data)[0]

    @classmethod
    def set_root_index(cls, index):
        with open(cls.storage, "rb+") as storage:
            storage.seek(NodeStream.len_size)
            storage.write(struct.pack(">i", index))

    @classmethod
    def set_node(cls, node):
        if not isinstance(node, Node):
            raise TypeError("Expected node")
        if node.index == -1:
            return None
        with open(cls.storage, "rb+") as storage:
            storage.seek(
                node.index * cls.size_row + NodeStream.len_size
                + NodeStream.root_pointer_size, 0)
            storage.writelines([
                struct.pack(">i", node.index),
                struct.pack(
                    ">i", -1 if isinstance(node.left, ImagineNode)
                    else node.left.index),
                struct.pack(
                    ">i", -1 if isinstance(node.right, ImagineNode)
                    else node.right.index),
                struct.pack(
                    ">i", -1 if isinstance(node.parent, ImagineNode)
                    else node.parent.index),
                NodeColor.to_byte(node.color),
                struct.pack(">i", node.key),
                struct.pack(">i", node.value)
            ])

    @classmethod
    def set_attribute(cls, offset, mask, index, value):
        with open(cls.storage, "rb+") as storage:
            storage.seek(
                index * cls.size_row + NodeStream.len_size
                + NodeStream.root_pointer_size + offset, 0)
            storage.write(struct.pack(mask, value))


class Node:
    def __init__(self, index, key, value, left=-1,
                 right=-1, parent=-1, color=NodeColor.Red):
        self.index = index
        self.key = key
        self.value = value
        self._color = color
        self._parent = parent
        self._left = left
        self._right = right

    @property
    def parent(self):
        node = NodeStream.get_node(self._parent)
        return node if node else ImagineNode()

    @parent.setter
    def parent(self, node):
        self._parent = node.index
        NodeStream.set_attribute(12, ">i", self.index, node.index)

    @property
    def left(self):
        node = NodeStream.get_node(self._left)
        return node if node else ImagineNode()

    @left.setter
    def left(self, node):
        self._left = node.index
        NodeStream.set_attribute(4, ">i", self.index, node.index)

    @property
    def right(self):
        node = NodeStream.get_node(self._right)
        return node if node else ImagineNode()

    @right.setter
    def right(self, node):
        self._right = node.index
        NodeStream.set_attribute(8, ">i", self.index, node.index)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        if not isinstance(color, NodeColor):
            raise TypeError("Expected color")
        self._color = color
        NodeStream.set_attribute(
            16, ">?", self.index, NodeColor.to_bool(color))

    def __eq__(self, other):
        if not isinstance(other, Node):
            raise TypeError("Expected node")
        return self.index == other.index

    def __bool__(self):
        return self.index != -1


class ImagineNode(Node):
    def __init__(self):
        super().__init__(
            -1, -1, -1, color=NodeColor.Black)


class Tree:
    def __init__(self, storage):
        NodeStream.storage = storage
        self.root = None

    def grandparent(self, node):
        if node and node.parent:
            return node.parent.parent

    def uncle(self, node):
        g = self.grandparent(node)
        if not g:
            return g
        if node.parent == g.left:
            return g.right
        return g.left

    def sibling(self, node):
        if node == node.parent.left:
            return node.parent.right
        return node.parent.left

    def replace_node(self, node_1, node_2):
        node_2.parent = node_1.parent
        if not node_1.parent:
            self.root = node_2
            NodeStream.set_node(self.root)
            NodeStream.set_root_index(self.root.index)
            return
        if node_1 == node_1.parent.left:
            node_1.parent.left = node_2
        else:
            node_1.parent.right = node_2

    def rotate_left(self, node):
        pivot = node.right
        pivot.parent = node.parent
        if node.parent:
            if node.parent.left == node:
                node.parent.left = pivot
            else:
                node.parent.right = pivot

        node.right = pivot.left
        if pivot.left:
            pivot.left.parent = node

        node.parent = pivot
        pivot.left = node

        if not pivot.parent:
            self.root = pivot
            NodeStream.set_node(self.root)
            NodeStream.set_root_index(self.root.index)

    def rotate_right(self, node):
        pivot = node.left
        pivot.parent = node.parent
        if node.parent:
            if node.parent.left == node:
                node.parent.left = pivot
            else:
                node.parent.right = pivot

        node.left = pivot.right
        if pivot.right:
            pivot.right.parent = node

        node.parent = pivot
        pivot.right = node

        if not pivot.parent:
            self.root = pivot
            NodeStream.set_node(self.root)
            NodeStream.set_root_index(self.root.index)

    def insert(self, key, value):
        root_index = NodeStream.get_root_index()
        self.root = NodeStream.get_node(root_index)
        if not self.root:
            self.root = Node(0, key, value, color=NodeColor.Black)
            NodeStream.set_node(self.root)
            NodeStream.nodes_count_up(0)
            NodeStream.set_root_index(0)
            return

        node = self.root
        while True:
            index = NodeStream.nodes_count()
            if value < node.value:
                if not node.left:
                    NodeStream.nodes_count_up(index)
                    _node = Node(index, key, value)
                    NodeStream.set_node(_node)
                    _node.parent = node
                    node.left = _node
                    self._insert_case1(_node)
                    break
                node = node.left

            else:
                if not node.right:
                    if value != node.value:
                        NodeStream.nodes_count_up(index)
                    else:
                        index = node.index
                    _node = Node(index, key, value)
                    NodeStream.set_node(_node)
                    _node.parent = node
                    node.right = _node
                    self._insert_case1(_node)
                    break
                node = node.right

    def _insert_case1(self, node):
        if not node.parent:
            node.color = NodeColor.Black
        else:
            self._insert_case2(node)

    def _insert_case2(self, node):
        if node.parent.color == NodeColor.Black:
            return
        else:
            self._insert_case3(node)

    def _insert_case3(self, node):
        u = self.uncle(node)
        if u and u.color == NodeColor.Red:
            node.parent.color = NodeColor.Black
            u.color = NodeColor.Black
            g = self.grandparent(node)
            g.color = NodeColor.Red
            self._insert_case1(g)
        else:
            self._insert_case4(node)

    def _insert_case4(self, node):
        g = self.grandparent(node)
        if node == node.parent.right \
                and node.parent == g.left:
            self.rotate_left(node.parent)
            node = node.left

        elif node == node.parent.left \
                and node.parent == g.right:
            self.rotate_right(node.parent)
            node = node.right

        self._insert_case5(node)

    def _insert_case5(self, node):
        g = self.grandparent(node)
        node.parent.color = NodeColor.Black
        g.color = NodeColor.Red

        if node == node.parent.left \
                and node.parent == g.left:
            self.rotate_right(g)
        else:
            self.rotate_left(g)

    def delete(self, value):
        node = self.find(value)
        if not node:
            return

        rm_node = node
        if node.left and node.right:
            rm_node = node.right
            while rm_node.left:
                rm_node = rm_node.left
            node.value = rm_node.value

        if rm_node.color == NodeColor.Red:
            if rm_node == rm_node.parent.left:
                rm_node.parent.left = ImagineNode()
            else:
                rm_node.parent.right = ImagineNode()

        elif rm_node.color == NodeColor.Black:
            child = rm_node.left or rm_node.right
            if child and child.color == NodeColor.Red:
                child.color = NodeColor.Black
                self.replace_node(rm_node, child)
            else:
                self._delete_case1(rm_node)

    def _delete_case1(self, node):
        if node.parent:
            self._delete_case2(node)
        else:
            self.root = ImagineNode()
            NodeStream.set_node(self.root)

    def _delete_case2(self, node):
        s = self.sibling(node)
        if s.color == NodeColor.Red:
            node.parent.color = NodeColor.Red
            s.color = NodeColor.Black
            if node == node.parent.left:
                self.rotate_left(node.parent)
            else:
                self.rotate_right(node.parent)
        self._delete_case3(node)

    def _delete_case3(self, node):
        s = self.sibling(node)
        if node.parent.color == NodeColor.Black \
                and s.color == NodeColor.Black \
                and s.left.color == NodeColor.Black \
                and s.right.color == NodeColor.Black:
            s.color = NodeColor.Red
            self._delete_case1(node.parent)
        else:
            self._delete_case4(node)

    def _delete_case4(self, node):
        s = self.sibling(node)
        if node.parent.color == NodeColor.Red \
                and s.color == NodeColor.Black \
                and s.left.color == NodeColor.Black \
                and s.right.color == NodeColor.Black:
            s.color = NodeColor.Red
            node.parent.color = NodeColor.Black
        else:
            self._delete_case5(node)

    def _delete_case5(self, node):
        s = self.sibling(node)
        if s.color == NodeColor.Black:
            if node == node.parent.left \
                    and s.right.color == NodeColor.Black \
                    and s.left.color == NodeColor.Red:
                s.color = NodeColor.Red
                s.left.color = NodeColor.Black
                self.rotate_right(s)
            elif node == node.parent.right \
                    and s.left.color == NodeColor.Black \
                    and s.right.color == NodeColor.Red:
                s.color = NodeColor.Red
                s.right.color = NodeColor.Black
                self.rotate_left(s)
        self._delete_case6(node)

    def _delete_case6(self, node):
        s = self.sibling(node)
        s.color = node.parent.color
        node.parent.color = NodeColor.Black

        if node == node.parent.left:
            s.right.color = NodeColor.Black
            self.rotate_left(node.parent)
        else:
            s.left.color = NodeColor.Black
            self.rotate_right(node.parent)

    def find(self, value):
        root_index = NodeStream.get_root_index()
        self.root = NodeStream.get_node(root_index)
        if not self.root:
            return

        node = self.root
        while node:
            if value == node.value:
                return node

            if value < node.value:
                node = node.left
            else:
                node = node.right

    def _search(self, node):
        yield str(node)
        if node.left:
            yield self._search(node.left)
        if node.right:
            yield self._search(node.right)

    def __iter__(self):
        if not self.root:
            raise StopIteration

        left = list()
        right = list()
        node = self.root
        if node.left:
            left = list(self._search(node.left))
        if node.right:
            right = list(self._search(node.right))
        return iter(chain([str(node)], left, right))
