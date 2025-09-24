from enum import Enum, auto
from typing import Generator, Iterator

from pads import Pads
from shapes import get_shape_slots


class Orientations(Enum):
    R0 = auto()
    R1 = auto()
    R2 = auto()
    R3 = auto()
    F0 = auto()
    F1 = auto()
    F2 = auto()
    F3 = auto()

    def __str__(self):
        return self.name


class Piece:

    def __init__(self, color: str, index: int, orientation: Orientations = Orientations.R0):
        self._color = color
        self._index = index
        self._orientation = orientation
        self._edge = Pads[color][index]

    @property
    def orientation(self) -> Orientations:
        return self._orientation

    @orientation.setter
    def orientation(self, orientation: Orientations):
        self._orientation = orientation

    @property
    def edge(self):
        edge = self._edge
        match self._orientation:
            case Orientations.R0:
                return edge
            case Orientations.R1:
                return edge[12:] + edge[:12]
            case Orientations.R2:
                return edge[8:] + edge[:8]
            case Orientations.R3:
                return edge[4:] + edge[:4]
            case Orientations.F0:
                return edge[4::-1] + edge[:4:-1]
            case Orientations.F1:
                return edge[8::-1] + edge[:8:-1]
            case Orientations.F2:
                return edge[12::-1] + edge[:12:-1]
            case Orientations.F3:
                return edge[0::-1] + edge[:0:-1]

    @property
    def color(self):
        return self._color

    @property
    def index(self):
        return self._index

    def __str__(self):
        symbols = ['   ', ' ┌─', '─┐ ', '───', ' └─', ' │ ', '─┼─', '─┘ ']

        e = self.edge
        # @formatter:off
        m = [
            [0,     0,     0,     0,    0,    0, 0],
            [0,  e[0],  e[1],  e[2], e[3], e[4], 0],
            [0, e[15],     1,     1,    1, e[5], 0],
            [0, e[14],     1,     1,    1, e[6], 0],
            [0, e[13],     1,     1,    1, e[7], 0],
            [0, e[12], e[11], e[10], e[9], e[8], 0],
            [0,     0,     0,     0,    0,    0, 0],
        ]
        # @formatter:on

        def c(i, j):
            n = int(''.join(str(m[i - di][j - dj]) for di in (1, 0) for dj in (1, 0)), 2)
            k = n if n <= 7 else 15 ^ n
            return symbols[k]

        return '\n'.join(''.join(c(i, j) for j in range(7))[1:].rstrip() for i in range(7))

    def corners(self) -> int:
        return sum(i for i in self._edge[0::4])

    def mid_cubits(self) -> int:
        return sum(i for i in self._edge[2::4])

    def other_cubits(self) -> int:
        return sum(i for i in self._edge[1::2])


def filter_pieces(
        tiles: list[tuple[int, int, int, int]],
        pieces: list[tuple[str, int]],
        hints: list[tuple[int, str, int, str]] = None,
) -> Generator[list[tuple[str, int]], None, None]:
    piece_map = {(color, index): ((pc := Piece(color, index)).corners(), pc.mid_cubits(), pc.other_cubits())
                 for color, index in pieces}
    hints = hints or []
    pieces_in_hints = {(color, index) for _, color, index, _ in hints}
    pieces = [piece for piece in pieces if piece not in pieces_in_hints]

    # cubit totals contributed by hints
    hints_cubits = tuple(sum(piece_map[(color, index)][i] for _, color, index, _ in hints) for i in range(3))

    slots = get_shape_slots(tiles, [])
    num_tiles = len(tiles)
    corners = {slots[tile * 16 + i] for tile in range(num_tiles) for i in range(0, 16, 4)}
    num_corners = len(corners)

    target_size = num_tiles - len(hints)
    target_c = num_corners - hints_cubits[0]
    target_m = 2 * num_tiles - hints_cubits[1]
    target_o = 4 * num_tiles - hints_cubits[2]

    memo = {}

    def dfs(i, corner_count, mid_count, other_count, size):
        state = i, corner_count, mid_count, other_count, size
        if state in memo:
            yield from memo[state]
            return

        memo[state] = []
        # Base case: exact match
        if size == target_size:
            if (corner_count, mid_count, other_count) == (target_c, target_m, target_o):
                memo[state].append(())
                yield ()
            return

        # Too many or out of pieces → dead end
        if any((
                i == len(pieces),  # no more pieces left
                corner_count > target_c,
                mid_count > target_m,
                other_count > target_o,
        )):
            return

        piece = pieces[i]
        pc, pm, po = piece_map[piece]
        # Option 1: skip piece
        for ss in dfs(i + 1, corner_count, mid_count, other_count, size):
            memo[state].append(ss)
            yield ss
        # Option 2: include piece
        for ss in dfs(i + 1, corner_count + pc, mid_count + pm, other_count + po, size + 1):
            memo[state].append((i, *ss))
            yield i, *ss

    for subset in dfs(0, 0, 0, 0, 0):
        yield [pieces[i] for i in subset]


def find_subsets(
        tiles: list[tuple[int, int, int, int]],
        pieces: list[tuple[str, int]],
        hints: list[tuple[int, str, int, str]] | None = None,
        tack_stitches: list | None = None,
) -> Generator[list[tuple[str, int]], None, None]:
    hints = hints or []
    tack_stitches = tack_stitches or []
    slots = get_shape_slots(tiles, tack_stitches)
    num_tiles = len(tiles)
    corners = {slots[tile * 16 + i] for tile in range(num_tiles) for i in range(0, 16, 4)}
    num_corners = len(corners)
    piece_map = {(color, index): ((pc := Piece(color, index)).corners(), pc.mid_cubits(), pc.other_cubits())
                 for color, index in pieces}
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


if __name__ == '__main__':
    piece = Piece('BLUE', 2)
    for orientation in Orientations:
        piece.orientation = orientation
        print(orientation)
        print(piece)