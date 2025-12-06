import signal
from collections.abc import Generator, Iterator
from enum import Enum
from functools import cache, wraps
from itertools import chain
from random import shuffle
from typing import Literal

from preloaded import Pads


class Orientations(Enum):
    R0 = (1, 0)
    R1 = (1, 12)
    R2 = (1, 8)
    R3 = (1, 4)
    F0 = (-1, 4)
    F1 = (-1, 8)
    F2 = (-1, 12)
    F3 = (-1, 0)

    def __init__(self, direction: int, offset: int):
        self._indexes = [(offset + direction * i) % 16 for i in range(16)]

    def apply_to(self, edge: list[int]):
        return (edge[i] for i in self._indexes)


@cache
def get_edge(color: str, index: int) -> list[int]:
    """Returns the edge of the piece with given index of given pad"""
    c = str(index)
    lines = Pads[color].value.splitlines()
    row_min = next(i for i, row in enumerate(lines) if c in row)
    row_max = row_min + 4
    col_min = 100
    for i, row in enumerate(lines[row_min: row_max + 1], start=row_min):
        col_start = next(j for j, v in enumerate(row) if v == c)
        col_min = min(col_min, col_start)
    col_max = col_min + 4
    return list(chain(
        (int(lines[row_min][i] == c) for i in range(col_min, col_max)),
        (int(lines[i][col_max] == c) for i in range(row_min, row_max)),
        (int(lines[row_max][i] == c) for i in range(col_max, col_min, -1)),
        (int(lines[i][col_min] == c) for i in range(row_max, row_min, -1)),
    ))


def get_shape_slots(
        tiles: list[tuple[int, int, int, int]],
        tack_stitches: list[tuple[int, int]] or None = None,
) -> list[int]:
    num_tiles = len(tiles)
    res = list(range(num_tiles * 16))

    def find(i):
        if res[i] == i:
            return i
        root = find(res[i])
        res[i] = root
        return root

    def union(i, j):
        i = find(i)
        j = find(j)
        if i != j:
            res[i] = j

    for tile1, neighbors in enumerate(tiles):
        for edge1, tile2 in enumerate(neighbors):
            if tile2 > tile1:
                edge2 = next(i for i, v in enumerate(tiles[tile2]) if v == tile1)
                for i in range(5):
                    slot1 = 16 * tile1 + (4 * edge1 + i) % 16
                    slot2 = 16 * tile2 + (4 * edge2 + 4 - i) % 16
                    union(slot1, slot2)
    if tack_stitches:
        for s1, s2 in tack_stitches:
            union(s1, s2)

    for i in range(len(res)):
        find(i)

    return res


class Node:
    def __init__(self, up, down, left, right, column=None, row_idx=None):
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


type Edge = list[Literal[0, 1]]


def filter_pieces(
        shape: list[tuple[int, int, int, int]],
        pieces: list[tuple[str, int]],
        hints: list[tuple[int, str, int, str]] | None = None,
        tack_stitches: list[tuple[int, int]] = None,
) -> Generator[list[tuple[str, int]], None, None]:
    hints = hints or []
    slots = get_shape_slots(shape, tack_stitches)
    num_tiles = len(shape)
    corners = {slots[tile * 16 + i] for tile in range(num_tiles) for i in range(0, 16, 4)}
    num_corners = len(corners)
    piece_map = {(color, index): (sum(i for i in edge[0::4]), sum(i for i in edge[2::4]), sum(i for i in edge[1::2]))
                 for color, index in pieces for edge in (get_edge(color=color, index=index),)}
    # cubit totals contributed by hints
    hints_cubits = tuple(sum(piece_map[(color, index)][i] for _, color, index, _ in hints) for i in range(3))

    target_pieces = num_tiles - len(hints)
    target_corners = num_corners - hints_cubits[0]
    target_mid = 2 * num_tiles - hints_cubits[1]
    target_other = 4 * num_tiles - hints_cubits[2]
    pieces_in_hints = {(color, index) for _, color, index, _ in hints}
    pieces = [piece for piece in pieces if piece not in pieces_in_hints]
    n = len(pieces)
    cs, ms, os = zip(*(piece_map[p] for p in pieces))
    # Optional: reorder 'pieces' by a heuristic (e.g., descending c+m+o)
    order = sorted(range(n), key=lambda i: (cs[i] + ms[i] + os[i]), reverse=True)
    pieces = [pieces[i] for i in order]
    cs = [cs[i] for i in order]
    ms = [ms[i] for i in order]
    os = [os[i] for i in order]

    # Suffix sums for reachability pruning (upper bounds)
    sc = [0] * (n + 1)
    sm = [0] * (n + 1)
    so = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        sc[i] = sc[i + 1] + cs[i]
        sm[i] = sm[i + 1] + ms[i]
        so[i] = so[i + 1] + os[i]

    dead = set()  # memo of dead states

    def dfs(i: int, k: int, c: int, m: int, o: int, chosen: tuple) -> Iterator[tuple]:
        state = (i, k, c, m, o)
        if state in dead:
            return

        # success
        if k == target_pieces:
            if c == target_corners and m == target_mid and o == target_other:
                yield chosen
            else:
                dead.add(state)
            return

        # out or not enough remaining
        if i == n or n - i < target_pieces - k:
            dead.add(state)
            return

        # overshoot
        if c > target_corners or m > target_mid or o > target_other:
            dead.add(state)
            return

        # unreachable even taking everything left
        if c + sc[i] < target_corners or m + sm[i] < target_mid or o + so[i] < target_other:
            dead.add(state)
            return

        found = False

        # include
        for sol in dfs(i + 1, k + 1, c + cs[i], m + ms[i], o + os[i], chosen + (pieces[i],)):
            found = True
            yield sol

        # skip
        for sol in dfs(i + 1, k, c, m, o, chosen):
            found = True
            yield sol

        if not found:
            dead.add(state)

    yield from dfs(0, 0, 0, 0, 0, tuple())


class Problem:

    def __init__(
            self,
            shape: list[tuple[int, int, int, int]],
            pieces: list[tuple[str, int]],
            hints: list[tuple[int, str, int, str]],
            tack_stitches: list[tuple[int, int]],
    ):
        self._num_tiles = len(shape)
        self._pieces = pieces
        self._slots = get_shape_slots(shape, tack_stitches)
        self._hints = hints
        self._assigned = self._get_assigned()
        self._row_mapping = []
        self._head = self._load_problem()

    def _get_assigned(self):
        assigned_tiles = set()
        assigned_pieces = set()
        assigned_slots = set()
        if self._hints:
            for tile, color, index, orientation_str in self._hints:
                assigned_tiles.add(tile)
                assigned_pieces.add((color, index))
                edge = Orientations[orientation_str].apply_to(get_edge(color, index))
                assigned_slots |= {self._slots[tile * 16 + i] for i, v in enumerate(edge) if v == 1}
        return assigned_pieces, assigned_slots, assigned_tiles

    def _get_unassigned(self):
        assigned_pieces, assigned_slots, assigned_tiles = self._assigned
        tiles = [tile for tile in range(self._num_tiles) if tile not in assigned_tiles]
        pieces = [pc for pc in self._pieces if pc not in assigned_pieces]
        shuffle(pieces)
        slots = set(self._slots) - assigned_slots
        return pieces, slots, tiles

    def _get_matrix(self, pieces, slots, tiles):
        rows = []
        slot_map = {j: i for i, j in enumerate(slots)}
        for tile in tiles:
            for piece_column, (color, index) in enumerate(pieces, start=len(slots)):
                edge = get_edge(color, index)
                rows_for_piece = set()
                for orientation in Orientations:
                    edge_ = orientation.apply_to(edge)
                    covered_slots = {self._slots[tile * 16 + i] for i, cubit in enumerate(edge_) if cubit == 1}
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
                    self._row_mapping.append((tile, color, index, orientation.name))
        return rows

    def _load_problem(self):

        pieces, slots, tiles = self._get_unassigned()
        # A column is True if primary and False if secondary
        columns = [True] * len(slots) + [False] * len(pieces)

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

    def solve(self) -> Generator[list, None, None]:
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
        shape: list[tuple[int, int, int, int]],
        pieces: list[tuple[str, int]],
        hints: list[tuple[int, str, int, str]] | None = None,
        tack_stitches: list = None,
):
    @time_guard(timeout=1)  # timeout in seconds
    def _solve():
        if len(pieces) > len(shape):
            piece_subsets = filter_pieces(shape, pieces, hints=hints, tack_stitches=tack_stitches)
            for piece_subset in piece_subsets:
                solution_ = next(Problem(shape, piece_subset, hints or [], tack_stitches or []).solve(), None)
                if solution_:
                    return solution_
        else:
            return next(Problem(shape, pieces, hints or [], tack_stitches or []).solve(), None)

    for tries in range(6):
        try:
            return _solve()
        except TimeoutError:
            pass
    return None


def timeout_handler(_signum, _frame):
    raise TimeoutError()


def time_guard(timeout: int = 1):
    """A decorator that raises an TimeoutError after `timeout` seconds unless the
    decorated function hasn't already returned."""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            try:
                result = f(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator
