# GENERAL EXACT COVER SOLVER
from collections.abc import Iterable


class Node(object):
    def __init__(self, up, down, left, right, column=None, row_idx=None):
        super().__init__()
        self.up = up
        self.down = down
        self.left = left
        self.right = right
        self.column = column
        self.row_idx = row_idx

    @staticmethod
    def row_iterator(node, reverse=False):
        """Iterates through all the nodes in a row."""
        start_node = node
        node = node.left if reverse else node.right
        while node != start_node:
            yield node
            node = node.left if reverse else node.right

    @staticmethod
    def column_iterator(node, reverse=False):
        """Iterates through all the nodes in a column."""
        start_node = node
        node = node.up if reverse else node.down
        while node != start_node:
            yield node
            node = node.up if reverse else node.down


class ColumnHead(Node):
    def __init__(self, left, right, primary: bool = True):
        super().__init__(self, self, left, right)
        self.primary = primary
        self.size = 0


class Head(Node):
    def __init__(self):
        super().__init__(self, self, self, self)


class ExactCover:

    def __init__(self, columns: Iterable[bool], rows: Iterable[Iterable[int]], clues: Iterable[int] | None= None):
        super().__init__()
        if clues is None:
            clues = []
        self._clues = clues
        # Add column headers
        head = Head()
        left_node = head
        column_heads: list[ColumnHead] = []
        for primary in columns:
            node = ColumnHead(left=left_node, right=None, primary=primary)
            left_node.right = node
            left_node = node
            column_heads.append(node)
        left_node.right = head
        head.left = left_node
        # Add rows
        for row_idx, row in enumerate(rows):
            first_node = left_node = None
            for column_head, v in zip(column_heads, row):
                if v:
                    up_node = column_head.up  # last node in column
                    node = Node(
                        up=up_node,
                        down=column_head,
                        left=left_node,
                        right=None,
                        column=column_head,
                        row_idx=row_idx,
                    )
                    if first_node is None:
                        first_node = node
                    up_node.down = node
                    if left_node:
                        left_node.right = node
                    column_head.up = node
                    left_node = node
                    column_head.size += 1
            left_node.right = first_node
            first_node.left = left_node
        self._head = head

    @property
    def head(self):
        return self._head

    @staticmethod
    def cover(column):
        column.right.left, column.left.right = column.left, column.right
        for i in Node.column_iterator(column):
            for j in Node.row_iterator(i):
                j.up.down, j.down.up = j.down, j.up
                if j.column.primary:
                    j.column.size -= 1

    @staticmethod
    def uncover(column):
        for i in Node.column_iterator(column, reverse=True):
            for j in Node.row_iterator(i, reverse=True):
                if j.column.primary:
                    j.column.size += 1
                j.up.down, j.down.up = j, j
        column.left.right, column.right.left = column, column

    def node_by_idx(self, row_idx_):
        for column_head in Node.row_iterator(self._head):
            for node in Node.column_iterator(column_head):
                if node.row_idx == row_idx_:
                    return node
        raise IndexError

    def solve(self):
        solution = []
        for node in (self.node_by_idx(i) for i in self._clues):
            self.cover(node.column)
            solution.append(node)
            for j in Node.row_iterator(node):
                self.cover(j.column)

        def search():

            try:
                selected_column = min((c for c in Node.row_iterator(self._head) if c.primary), key=lambda c: c.size)
            except ValueError:
                # No more columns to cover; problem solved
                yield [node.row_idx for node in solution]
            else:
                if selected_column.size == 0:
                    # No rows left to cover selected_column; solution not found
                    return
                self.cover(selected_column)
                for node in Node.column_iterator(selected_column):
                    solution.append(node)
                    for j in Node.row_iterator(node):
                        self.cover(j.column)
                    yield from search()
                    node = solution.pop()
                    for j in Node.row_iterator(node, reverse=True):
                        self.uncover(j.column)
                self.uncover(selected_column)

        return search()
