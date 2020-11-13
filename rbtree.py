from enum import Enum


class NodeColor(Enum):
    Black = "Black",
    Red = "Red"


class Node:
    def __init__(self, value, color=NodeColor.Red):
        self.value = value
        self.color = color
        self.parent = None
        self.left = None
        self.right = None

    def __str__(self):
        return f"{self.color.name} | {self.value}"


class Tree:
    def __init__(self):
        self.root = None

    def grandparent(self, node):
        if node and node.parent:
            return node.parent.parent

    def uncle(self, node):
        g = self.grandparent(node)
        if not g:
            return None
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

    def insert(self, value):
        if not self.root:
            node = Node(value, color=NodeColor.Black)
            self.root = node
            return

        node = self.root
        while True:
            if value < node.value:
                if not node.left:
                    _node = Node(value)
                    _node.parent = node
                    node.left = _node
                    self._insert_case1(_node)
                    break
                node = node.left

            else:
                if not node.right:
                    _node = Node(value)
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
                rm_node.parent.left = None
            else:
                rm_node.parent.right = None

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
            self.root = None

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
