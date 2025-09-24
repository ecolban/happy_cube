import time
from collections import defaultdict
from itertools import chain
from random import shuffle
from typing import Iterable

from pads import Pads
from pieces import Piece, Orientations, filter_pieces, find_subsets
from shapes import Shapes, get_shape_slots
from test_happy_cube import check_solution


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
            tack_stitches: list[tuple[int, int]]
    ):
        self._num_tiles = len(tiles)
        self._pieces = pieces
        self._slots = get_shape_slots(tiles, tack_stitches)
        self._hints = hints
        self._assigned = self._get_assigned()
        self._row_mapping = []
        self._head = self._load_problem()

    def _get_assigned(self):
        assigned_tiles = set()
        assigned_pieces = set()
        assigned_slots = set()
        if self._hints:
            for tile, pc_color, pc_idx, orientation_str in self._hints:
                assigned_tiles.add(tile)
                assigned_pieces.add((pc_color, pc_idx))
                piece = Piece(pc_color, pc_idx, Orientations[orientation_str])
                assigned_slots |= {self._slots[tile * 16 + i] for i, v in enumerate(piece.edge) if v == 1}
        return assigned_pieces, assigned_slots, assigned_tiles

    def _get_unassigned(self):
        assigned_pieces, assigned_slots, assigned_tiles = self._assigned
        tiles = [tile for tile in range(self._num_tiles) if tile not in assigned_tiles]
        pieces = [pc for pc in self._pieces if (pc.color, pc.index) not in assigned_pieces]
        slots = set(self._slots) - assigned_slots
        return pieces, slots, tiles

    def _get_matrix(self, pieces, slots, tiles):
        rows = []
        slot_map = {j: i for i, j in enumerate(slots)}
        for tile in tiles:
            for piece_column, piece in enumerate(pieces, start=len(slots)):
                rows_for_piece = set()
                for orientation in Orientations:
                    piece.orientation = orientation
                    covered_slots = {self._slots[tile * 16 + i] for i, cubit in enumerate(piece.edge) if cubit == 1}
                    if not covered_slots <= slots:
                        continue
                    row = [0] * (len(slots) + len(pieces))
                    for slot in covered_slots:
                        row[slot_map[slot]] = 1
                    row[piece_column] = 1
                    if tuple(row) in rows_for_piece:
                        continue
                    rows_for_piece.add(tuple(row))
                    rows.append(row)
                    self._row_mapping.append((tile, piece.color, piece.index, orientation.name))
        return rows

    def _load_problem(self):

        pieces, slots, tiles = self._get_unassigned()
        # A column is True if primary and False if secondary
        columns = [True] * len(slots) + [len(pieces) == len(tiles)] * len(pieces)

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
        rows = self._get_matrix(pieces, slots, tiles)
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

    def update_pieces(self, pieces: list[Piece]):
        self._pieces = pieces
        self._row_mapping = []
        self._head = self._load_problem()

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


def solve(
        tiles: list[tuple[int, int, int, int]],
        pieces: list[tuple[str, int]],
        tack_stitches: list[tuple[int, int]] | None = None,
        hints: list[tuple[int, str, int, str]] | None = None,
):
    piece_objs = [Piece(color, index) for color, index in pieces]
    problem = Problem(tiles, piece_objs, hints or [], tack_stitches or [])
    return problem.solve()


def print_solution(solution, name=None):
    if name:
        print(name)
    print(', '.join(str(x) for x in solution))
    for tile, color, index, orientation_str in solution:
        print(f'{tile}: {color}[{index}]')
        p = Piece(color, index)
        p.orientation = Orientations[orientation_str]
        print(p)


def three_d_cross():
    shape = Shapes.THREE_D_CROSS
    # tiles = shape_shuffle(shape.tiles)
    tiles = shape.tiles
    pieces = [(pad.name, i) for pad in Pads for i in range(1, 7)]
    shuffle(pieces)
    hints = [
        # (2, 'GREEN', 2, 'R0'),
    ]
    solvable = find_subsets(tiles, pieces, hints=hints)
    # solvable = list(find_subsets(tiles, pieces, hints=hints))
    # always_used = set(pieces).intersection(*(set(pcs) for pcs in solvable))
    # print(len(always_used), ','.join(f'{color}[{index}]' for color, index in sorted(always_used)))
    # never_used = set(pieces) - set().union(*(set(pcs) for pcs in solvable))
    # print(len(never_used), ','.join(f'{color}[{index}]' for color, index in sorted(never_used)))
    # sometimes_used = set(pieces) - always_used.union(never_used)
    # print(len(sometimes_used), ','.join(f'{color}[{index}]' for color, index in sorted(sometimes_used)))

    for pcs in solvable:
        solution = next(solve(tiles, pcs, hints=hints), None)
        if solution:
            check_solution(tiles, set(pieces), tack_stitches=[], solution=solution)
            return solution


def cube_with_2_inverted_vertices():
    tiles = Shapes.CUBE_2x2x2_WITH_TWO_INVERTED_VERTICES.tiles
    pieces = [(color, idx) for color in ('BLUE', 'PINK', 'YELLOW', 'RED', 'PURPLE') for idx in range(1, 7)]
    shuffle(pieces)
    tack_stitches = [(8 * 16 + 0, 19 * 16 + 4)]
    hints = []
    solvable = find_subsets(tiles, pieces, hints=hints, tack_stitches=tack_stitches)
    for pcs in solvable:
        solution = next(solve(tiles, pcs, hints=hints, tack_stitches=tack_stitches), None)
        if solution:
            check_solution(tiles, set(pieces), tack_stitches=tack_stitches, solution=solution)
            return solution


def cube_2_by_2_by_2_w_outgrowth():
    tiles = Shapes.CUBE_2x2x2_WITH_CUBE_1x1x1_OUTGROWTH.tiles
    pieces = [(pad.name, i) for pad in Pads for i in range(1, 7) if pad.name != 'GREEN' or i != 5]
    hints = None

    shuffle(pieces)
    return next(solve(tiles, pieces, hints=hints), None)


def cube_2_by_2_by_2():
    tiles = Shapes.CUBE_2x2x2.tiles
    pieces = [(pad.name, i) for pad in Pads for i in range(1, 7) if pad.name != 'GREEN' or i != 5]
    hints = None

    shuffle(pieces)
    return next(solve(tiles, pieces, hints=hints), None)


def two_cube_with_tack_stitch():
    tiles = Shapes.TWO_CUBE_1x1x1.tiles
    pieces = [(pad.name, i) for pad in Pads for i in range(1, 7)]
    shuffle(pieces)
    tack_stitches = [(2 * 16 + 0, 8 * 16 + 0)]
    return next(solve(tiles, pieces, tack_stitches=tack_stitches), None)


def three_cube_with_tack_stitches():
    tiles = Shapes.THREE_CUBE_1x1x1.tiles
    pieces = [(pad.name, i) for pad in Pads for i in range(1, 7)]
    shuffle(pieces)
    tack_stitches = [(0 * 16 + 0, 6 * 16 + 0), (6 * 16 + 8, 12 * 16 + 0)]
    return next(solve(tiles, pieces, tack_stitches=tack_stitches), None)


def four_cube_with_tack_stitches():
    tiles = Shapes.FOUR_CUBE_1x1x1.tiles
    pieces = [(pad.name, i) for pad in Pads for i in range(1, 7)]
    shuffle(pieces)
    tack_stitches = [(0 * 16 + 0, 6 * 16 + 0), (6 * 16 + 8, 12 * 16 + 0), (6 * 16 + 4, 18 * 16 + 0)]
    return next(solve(tiles, pieces, tack_stitches=tack_stitches), None)


def five_cube_with_tack_stitches():
    tiles = Shapes.FIVE_CUBE_1x1x1.tiles
    pieces = [(pad.name, i) for pad in Pads for i in range(1, 7)]
    shuffle(pieces)
    tack_stitches = [
        (0 * 16 + 0, 6 * 16 + 0),
        (0 * 16 + 4, 12 * 16 + 0),
        (0 * 16 + 8, 18 * 16 + 0),
        (0 * 16 + 12, 24 * 16 + 0),
    ]
    return next(solve(tiles, pieces, tack_stitches=tack_stitches), None)


def simple_cube():
    tiles = Shapes.CUBE_1x1x1.tiles
    pieces = [(color, i) for color in ('PURPLE',) for i in range(1, 7)]
    shuffle(pieces)
    return next(solve(tiles, pieces), None)


def simple_prism():
    tiles = Shapes.PRISM_1x1x2.tiles
    pieces = [(pad.name, i) for pad in Pads for i in range(1, 7)]
    shuffle(pieces)
    return next(solve(tiles, pieces), None)


def three_cube():
    tiles = Shapes.THREE_CUBE_1x1x1.tiles
    pieces = [(color, i) for color in ('BLUE', 'GREEN', 'PINK') for i in range(1, 7)]
    shuffle(pieces)
    for pcs in find_subsets(tiles, pieces):
        return next(solve(tiles, pcs), None)


def three_steps():
    tiles = Shapes.THREE_STEPS.tiles
    pieces = [(pad.name, i) for pad in Pads for i in range(1, 7) if (pad.name, i) != ('GREEN', 2)]
    hints = []
    shuffle(pieces)
    return next(solve(tiles, pieces, hints), None)


def main(problem, name):
    start = time.time()
    solution = problem()
    if solution:
        print_solution(solution, name)
    else:
        print("No solution found.")
    print(f'Time = {int((time.time() - start) * 1000)} ms')


if __name__ == '__main__':
    # main(five_cube_with_tack_stitches, "4 Cube with tack stitches")
    # main(three_d_cross, "3D Cross")
    # main(three_steps, "3 Steps")
    # main(cube_2_by_2_by_2_w_outgrowth, "2x2x2 with Outgrowth")
    # main(cube_2_by_2_by_2, "2x2x2 cube")
    # main(simple_cube, "Simple cube")
    # main(simple_prism, "Simple prism")
    # main(two_cube_with_tack_stitch, "2 cubes tacked together")
    # main(cube_with_2_inverted_vertices, "2x2x2 cube with inverted vertices")
    main(three_d_cross, "3D cross")
