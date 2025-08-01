import re
import time
from collections import defaultdict
from typing import Iterable

from pads import Pads
from pieces import Piece, Orientations
from puzzles import Shapes, get_cubits, filter_pieces


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
        self._cubits = get_cubits(tiles)
        self._hints = hints
        self._row_mapping = {}
        self._head = self.load_problem()
        self._hints = hints

    def get_matrix(self):

        row_id = 0
        rows = []
        ignored_tiles = set()
        ignored_pieces = set()
        ignored_cubits = set()
        if self._hints:
            for tile, pc_color, pc_idx, orientation_str in self._hints:
                ignored_tiles.add(tile)
                ignored_pieces.add((pc_color, pc_idx))
                piece = Piece(Pads[pc_color], pc_idx)
                piece.orientation = Orientations[orientation_str]
                ignored_cubits |= {self._cubits[tile * 16 + i] for i, v in enumerate(piece.edge) if v == 1}
        tiles = [tile for tile in range(self._num_tiles) if tile not in ignored_tiles]
        pieces = [pc for pc in self._pieces if (pc.color, pc.index) not in ignored_pieces]
        cubits = set(self._cubits) - ignored_cubits
        cubit_map = {j: i for i, j in enumerate(cubits)}
        columns = [True] * len(cubits) + [False] * len(pieces)
        num_primary_cols = len(cubits)
        for tile in tiles:
            for i, piece in enumerate(pieces):
                rows_for_piece = set()
                for orientation in Orientations:
                    piece.orientation = orientation
                    cubit_set = {self._cubits[tile * 16 + i] for i, v in enumerate(piece.edge) if v == 1}
                    if not cubit_set <= cubits:
                        continue
                    row = [0] * len(columns)
                    for cubit in cubit_set:
                        row[cubit_map[cubit]] = 1
                    row[num_primary_cols + i] = 1
                    if tuple(row) in rows_for_piece:
                        continue
                    rows_for_piece.add(tuple(row))
                    rows.append(row)
                    self._row_mapping[row_id] = (tile, piece, orientation)
                    row_id += 1
        return columns, rows

    def load_problem(self):

        columns, rows = self.get_matrix()
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
                yield sorted(self._row_mapping[node.row_idx] for node in solution)
            else:
                if selected_column.size == 0:
                    # No rows left to cover selected_column; solution not found
                    return
                Problem.cover(selected_column)
                for node in Node.column_iterator(selected_column):
                    solution.append(node)
                    for j in Node.row_iterator(node):
                        Problem.cover(j.column)
                    yield from search()
                    node = solution.pop()
                    for j in Node.row_iterator(node, reverse=True):
                        Problem.uncover(j.column)
                Problem.uncover(selected_column)

        return search()


def check_solution(
        tiles: list[tuple[int, int, int, int]],
        pieces: set[tuple[str, int]],
        solution: Iterable[tuple[int, str, int, str]],
) -> bool:
    res = True
    covered_tiles = set(tile for tile, *_ in solution)
    uncovered_tile = next((tile for tile, _ in enumerate(tiles) if tile not in covered_tiles), None)
    if uncovered_tile:
        print(f"Tile {uncovered_tile} has not been assigned any piece")
        res = False
    piece_assignment = defaultdict(list)
    for tile, color, index, _ in solution:
        piece_assignment[(color, index)].append(tile)
    reused_piece = next((p for p, v in piece_assignment.items() if len(v) > 1), None)
    if reused_piece:
        print(f"Piece {reused_piece} is used more than once.")
        res = False
    cubits = get_cubits(tiles)
    covered_cubits = defaultdict(list)
    for tile, color, index, orientation in solution:
        if (color, index) not in pieces:
            print(f"The solution uses {(color, index)}, which is not in the pieces for this problem.")
            res = False
        try:
            piece = Piece(Pads[color], index)
            piece.orientation = Orientations[orientation]
            for i, v in enumerate(piece.edge):
                if v == 1:
                    covered_cubits[cubits[16 * tile + i]].append((tile, color, index))
        except (IndexError, KeyError):
            res = False
    uncovered_cubit = next((cubit for cubit in cubits if cubit not in covered_cubits), None)
    if uncovered_cubit:
        tile, i = divmod(uncovered_cubit, 16)
        print(f"Cubit {i} of tile {tile} is not covered by any piece.")
        res = False
    collision = next((cubit for cubit, v in covered_cubits.items() if len(v) > 1), None)
    if collision:
        tile, i = divmod(collision, 16)
        a = ' and '.join(f"piece {(color, index)} assigned to tile {tile}"
                         for tile, color, index in covered_cubits[collision])
        print(f"Cubit {i} of tile {tile} is covered by {a}")
        res = False
    return res


def read_problem6_pieces():
    def h(pad_str):
        m = re.match(r'([A-Z]+)\[(\d)]', pad_str)
        return m.group(1), int(m.group(2))

    with open('possible_piece_selection_problem6.csv', mode='r') as f:
        res = [[h(s) for s in line.split(',')] for line in f]
    return res


def solve(
        tiles: list[tuple[int, int, int, int]],
        pieces: list[Piece],
        hints: list[tuple[int, str, int, str]] = None,
):
    problem = Problem(tiles, pieces, hints)
    return ([(tile, p.color, p.index, orientation.name) for tile, p, orientation in a] for a in problem.solve())


def print_solution(solution, hints=None):
    if hints:
        solution.extend(hints)
    solution.sort()
    print(', '.join(str(x) for x in solution))
    used_pieces = set()
    for tile, color, index, orientation in solution:
        used_pieces.add((color, index))
        print(f'{tile}: {color}[{index}]')
        p = Piece(Pads[color], index)
        p.orientation = Orientations[orientation]
        print(p)

    unused_pieces = {(pad.name, i) for pad in Pads for i in range(6)} - used_pieces
    print(list(unused_pieces))
    end = time.time()
    return end


def main():
    start = time.time()
    hints = [
        (23, 'YELLOW', 1, 'F1'),
        (3, 'BLUE', 4, 'R1'),
        (5, 'PURPLE', 4, 'F2')
    ]
    shape = Shapes.SHAPE4
    pad_pieces = [
        ('BLUE', 0), ('BLUE', 2), ('BLUE', 3), ('BLUE', 4), ('BLUE', 5),
        ('ORANGE', 0), ('ORANGE', 1), ('ORANGE', 2), ('ORANGE', 4), ('ORANGE', 5),
        ('PURPLE', 3), ('PURPLE', 4), ('PURPLE', 5),
        ('RED', 0), ('RED', 2), ('RED', 3), ('RED', 4), ('RED', 5),
        ('YELLOW', 0), ('YELLOW', 1), ('YELLOW', 2), ('YELLOW', 3), ('YELLOW', 4), ('YELLOW', 5),
    ]
    pieces = [Piece(Pads[color], index) for color, index in pad_pieces]
    solution = next(solve(shape.tiles, pieces, hints))
    end = print_solution(solution, hints)
    print(f'Time = {int((end - start) * 1000)} ms')


def main2():
    start = time.time()
    tiles = Shapes.SHAPE8.tiles
    pieces = [Piece(pad, index) for pad in Pads for index in range(6)]
    pieces = next(filter_pieces(tiles, pieces))
    solution = next(solve(tiles, pieces))
    end = print_solution(solution)
    print(f'Time = {int((end - start) * 1000)} ms')


def main3():
    start = time.time()
    shape = Shapes.SHAPE1
    pad_pieces = [('RED', 5), ('PURPLE', 4), ('YELLOW', 4), ('PURPLE', 0), ('RED', 1), ('YELLOW', 0), ('RED', 4),
                  ('PURPLE', 2), ('RED', 0), ('YELLOW', 3), ('RED', 3), ('YELLOW', 5)]
    pieces = [Piece(Pads[color], index) for color, index in pad_pieces]
    solution = next(solve(shape.tiles, pieces))
    end = print_solution(solution)
    print(f'Time = {int((end - start) * 1000)} ms')


if __name__ == '__main__':
    main2()
