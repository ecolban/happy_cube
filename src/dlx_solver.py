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

    def row_iterator(self, reverse=False):
        start_node = self
        node = self.left if reverse else self.right
        while node != start_node:
            yield node
            node = node.left if reverse else node.right

    def column_iterator(self, reverse=False):
        """Iterates through all the nodes in a column."""
        start_node = self
        node = self.up if reverse else self.down
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


Solution = list[int]  # a list of the indices of the selected rows


class DlxSolver(Iterable[Solution]):

    def __init__(self, columns: Iterable[bool], rows: Iterable[Iterable[int]], clues: Iterable[int] | None = None):
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
        self._solutions = self._gen_solutions()

    @staticmethod
    def _cover(column):
        column.right.left, column.left.right = column.left, column.right
        for i in column.column_iterator():
            for j in i.row_iterator():
                j.up.down, j.down.up = j.down, j.up
                if j.column.primary:
                    j.column.size -= 1

    @staticmethod
    def _uncover(column):
        for i in column.column_iterator(reverse=True):
            for j in i.row_iterator(reverse=True):
                if j.column.primary:
                    j.column.size += 1
                j.up.down, j.down.up = j, j
        column.left.right, column.right.left = column, column

    def _node_by_idx(self, row_idx_):
        for column_head in self._head.row_iterator():
            for node in column_head.column_iterator():
                if node.row_idx == row_idx_:
                    return node
        raise IndexError

    def _gen_solutions(self):
        solution = []
        for node in (self._node_by_idx(i) for i in self._clues):
            self._cover(node.column)
            solution.append(node)
            for j in node.row_iterator():
                self._cover(j.column)

        def search():

            try:
                selected_column = min((c for c in self._head.row_iterator() if c.primary), key=lambda c: c.size)
            except ValueError:
                # No more columns to cover; problem solved
                yield [node.row_idx for node in solution]
            else:
                if selected_column.size == 0:
                    # No rows left to cover selected_column; solution not found
                    return
                self._cover(selected_column)
                for node in selected_column.column_iterator():
                    solution.append(node)
                    for j in node.row_iterator():
                        self._cover(j.column)
                    yield from search()
                    node = solution.pop()
                    for j in node.row_iterator(reverse=True):
                        self._uncover(j.column)
                self._uncover(selected_column)

        return search()

    def __next__(self):
        return next(self._solutions)

    def __iter__(self):
        return self
