import re
import time
from itertools import chain
from random import shuffle
from typing import Iterable

from pads import Pads
from pieces import Piece, Orientations
from shapes import Shapes, get_shape_slots, filter_pieces


class Node:
    def __init__(self, up, down, left, right, column=None, row_idx=None):
        self.up = up
        self.down = down
        self.left = left
        self.right = right
        self.column = column
        self.row_idx = row_idx

    @staticmethod
    def row_iterator(node, reverse=False, include_first=False):
        """Iterates through all the nodes in a row."""
        start_node = node
        if include_first:
            yield node
        node = node.left if reverse else node.right
        while node != start_node:
            yield node
            node = node.left if reverse else node.right

    @staticmethod
    def column_iterator(node, reverse=False, include_first=False):
        """Iterates through all the nodes in a column."""
        start_node = node
        if include_first:
            yield node
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


class Problem:

    def __init__(
            self,
            tiles: list[tuple[int, int, int, int]],
            pieces: list[Piece],
            hints: Iterable[tuple[int, str, int, str]],
    ):
        # self._tiles = tiles
        self._num_tiles = len(tiles)
        self._pieces = pieces
        self._slots = get_shape_slots(tiles)
        self._hints = hints
        self._row_mapping = {}
        self._head = self._load_problem()
        self._hints = hints or []

    def _get_matrix(self):

        row_idx = 0
        rows = []
        ignored_tiles = set()
        ignored_pieces = set()
        ignored_slots = set()
        if self._hints:
            for tile, pc_color, pc_idx, orientation_str in self._hints:
                ignored_tiles.add(tile)
                ignored_pieces.add((pc_color, pc_idx))
                piece = Piece(pc_color, pc_idx)
                piece.orientation = Orientations[orientation_str]
                ignored_slots |= {self._slots[tile * 16 + i] for i, v in enumerate(piece.edge) if v == 1}
        tiles = [tile for tile in range(self._num_tiles) if tile not in ignored_tiles]
        pieces = [pc for pc in self._pieces if (pc.color, pc.index) not in ignored_pieces]
        slots = set(self._slots) - ignored_slots
        slot_map = {j: i for i, j in enumerate(slots)}
        columns = [True] * len(slots) + [False] * len(pieces)
        for tile in tiles:
            for piece_column, piece in enumerate(pieces, start=len(slots)):
                rows_for_piece = set()
                for orientation in Orientations:
                    piece.orientation = orientation
                    slot_subset = {self._slots[tile * 16 + i] for i, cubit in enumerate(piece.edge) if cubit == 1}
                    if not slot_subset <= slots:
                        continue
                    row = [0] * len(columns)
                    for slot_column in slot_subset:
                        row[slot_map[slot_column]] = 1
                    row[piece_column] = 1
                    if tuple(row) in rows_for_piece:
                        continue
                    rows_for_piece.add(tuple(row))
                    rows.append(row)
                    self._row_mapping[row_idx] = (tile, piece.color, piece.index, orientation.name)
                    row_idx += 1
        return columns, rows

    def _load_problem(self):

        columns, rows = self._get_matrix()
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
                    up_node = column_head.up
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

        return head

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

    def solve(self):
        solution = []

        def search():
            try:
                selected_column = min((c for c in Node.row_iterator(self._head) if c.primary), key=lambda c: c.size)
            except ValueError:
                # No more columns to cover; problem solved
                yield sorted(chain(self._hints, (self._row_mapping[node.row_idx] for node in solution)))
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


def read_problem6_pieces():
    def h(pad_str):
        m = re.match(r'([A-Z]+)\[(\d)]', pad_str)
        return m.group(1), int(m.group(2))

    with open('possible_piece_selection_problem6.csv', mode='r') as f:
        res = [[h(s) for s in line.split(',')] for line in f]
    return res


def solve(
        shape: list[tuple[int, int, int, int]],
        pieces: list[tuple[str, int]],
        hints: list[tuple[int, str, int, str]] = None,
):
    piece_objs = [Piece(color, index) for color, index in pieces]
    problem = Problem(shape, piece_objs, hints)
    return problem.solve()


def print_solution(solution, hints=None):
    if hints:
        solution.extend(hints)
    solution.sort()
    print(', '.join(str(x) for x in solution))
    used_pieces = set()
    for tile, color, index, orientation in solution:
        used_pieces.add((color, index))
        print(f'{tile}: {color}[{index}]')
        p = Piece(color, index)
        p.orientation = Orientations[orientation]
        print(p)

    unused_pieces = {(pad.name, i) for pad in Pads for i in range(6)} - used_pieces
    print(list(unused_pieces))


def main():
    start = time.time()
    hints = [
        (23, 'YELLOW', 1, 'F1'),
        (3, 'BLUE', 4, 'R1'),
        (5, 'PURPLE', 4, 'F2')
    ]
    shape = Shapes.CUBE_2x2x2
    pad_pieces = [
        ('BLUE', 0), ('BLUE', 2), ('BLUE', 3), ('BLUE', 4), ('BLUE', 5),
        ('ORANGE', 0), ('ORANGE', 1), ('ORANGE', 2), ('ORANGE', 4), ('ORANGE', 5),
        ('PURPLE', 3), ('PURPLE', 4), ('PURPLE', 5),
        ('RED', 0), ('RED', 2), ('RED', 3), ('RED', 4), ('RED', 5),
        ('YELLOW', 0), ('YELLOW', 1), ('YELLOW', 2), ('YELLOW', 3), ('YELLOW', 4), ('YELLOW', 5),
    ]
    solution = next(solve(shape.tiles, pad_pieces, hints))
    print_solution(solution, hints)
    print(f'Time = {int((time.time() - start) * 1000)} ms')


def main2():
    start = time.time()
    shape = Shapes.CUBE_2x2x2_WITH_TWO_INVERTED_VERTICES.value
    pieces = [(pad.name, idx) for pad in Pads for idx in range(6)]
    shuffle(pieces)
    filtered_pieces = filter_pieces(shape, pieces)
    solution = next(s for s in (next(solve(shape, pcs), None) for pcs in filtered_pieces) if s is not None)
    if solution:
        print_solution(solution)
    else:
        print("No solution found!")
    print(f'Time = {int((time.time() - start) * 1000)} ms')


def main3():
    start = time.time()
    shape = Shapes.CUBE_2x2x2_WITH_TWO_INVERTED_VERTICES.value
    pieces = [(color, idx) for color in ('RED', 'PINK', 'YELLOW', 'BLUE', 'GREEN') for idx in range(6)]
    # hints = [(0, 'YELLOW', 1, 'R2'), (1, 'GREEN', 1, 'F3'), (2, 'PURPLE', 5, 'R1'), (3, 'YELLOW', 5, 'F1'),
    #          (4, 'BLUE', 2, 'ID'), (5, 'PURPLE', 1, 'F2'), (6, 'PURPLE', 0, 'R1')]
    hints = None
    shuffle(pieces)
    filtered_pieces = filter_pieces(shape, pieces, hints)
    solution = next(s for s in (next(solve(shape, pcs, hints), None) for pcs in filtered_pieces) if s is not None)
    if solution:
        print_solution(solution)
    else:
        print("No solution found!")
    print(f'Time = {int((time.time() - start) * 1000)} ms')


if __name__ == '__main__':
    main3()
