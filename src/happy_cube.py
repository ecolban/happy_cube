import re
import time
from collections import defaultdict
from enum import Enum
from functools import cache
from itertools import combinations
from typing import Optional, Iterable

N, E, S, W = 0, 1, 2, 3

#  0
# 123
#  4
#  5
PROBLEM1 = [
    (5, 3, 2, 1),
    (0, 2, 4, 5),
    (0, 3, 4, 1),
    (0, 5, 4, 2),
    (2, 3, 5, 1),
    (4, 3, 0, 1),
]
PROBLEM1x6 = [
    (5, 3, 2, 1),
    (0, 2, 4, 5),
    (0, 3, 4, 1),
    (0, 5, 4, 2),
    (2, 3, 5, 1),
    (4, 3, 0, 1),

    (11, 9, 8, 7),
    (6, 8, 10, 11),
    (6, 9, 10, 7),
    (6, 11, 10, 8),
    (8, 9, 11, 7),
    (10, 9, 6, 7),

    (17, 15, 14, 13),
    (12, 14, 16, 17),
    (12, 15, 16, 13),
    (12, 17, 16, 14),
    (14, 15, 17, 13),
    (16, 15, 12, 13),

    (23, 21, 20, 19),
    (18, 20, 22, 23),
    (18, 21, 22, 19),
    (18, 23, 22, 20),
    (20, 21, 23, 19),
    (22, 21, 18, 19),

    # (29, 27, 26, 25),
    # (24, 26, 28, 29),
    # (24, 27, 28, 25),
    # (24, 29, 28, 26),
    # (26, 27, 29, 25),
    # (28, 27, 24, 25),
    #
    # (35, 33, 32, 31),
    # (30, 32, 34, 35),
    # (30, 33, 34, 31),
    # (30, 35, 34, 32),
    # (32, 33, 35, 31),
    # (34, 33, 30, 31),
]
#  01
# 2345
#  67
#  89
PROBLEM2 = [
    (8, 1, 3, 2),
    (9, 5, 4, 0),
    (0, 3, 6, 8),
    (0, 4, 6, 2),
    (1, 5, 7, 3),
    (1, 9, 7, 4),
    (3, 7, 8, 2),
    (4, 5, 9, 6),
    (6, 9, 0, 2),
    (7, 5, 1, 8),
]
#  012
# 34567
#  89A
#  BCD
PROBLEM3 = [
    (11, 1, 4, 3),
    (12, 2, 5, 0),
    (17, 7, 6, 1),
    (0, 4, 8, 11),
    (0, 5, 8, 3),
    (1, 6, 9, 4),
    (2, 7, 10, 5),
    (2, 16, 10, 6),
    (4, 9, 11, 3),
    (5, 10, 12, 8),
    (6, 7, 13, 9),
    (8, 12, 0, 3),
    (9, 14, 1, 11),
    #  (10, 7, 2, 12),
    (10, 16, 15, 14),
    (13, 15, 17, 12),
    (13, 16, 17, 14),
    (13, 7, 17, 15),
    (15, 16, 2, 14),
]
#        0  1
#        2  3
#  4  5  6  7  8  9
# 10 11 12 13 14 15
#       16 17
#       18 19
#       20 21
#       22 23
PROBLEM4 = [
    (22, 1, 2, 4),
    (23, 9, 3, 0),
    (0, 3, 6, 5),
    (1, 8, 7, 2),
    (0, 5, 10, 22),
    (2, 6, 11, 4),
    (2, 7, 12, 5),
    (3, 8, 13, 6),
    (3, 9, 14, 7),
    (1, 23, 15, 8),
    (4, 11, 18, 20),
    (5, 12, 16, 10),
    (6, 13, 16, 11),
    (7, 14, 17, 12),
    (8, 15, 17, 13),
    (9, 21, 19, 14),
    (12, 17, 18, 11),
    (13, 14, 19, 16),
    (16, 19, 20, 10),
    (17, 15, 21, 18),
    (18, 21, 22, 10),
    (19, 15, 23, 20),
    (20, 23, 0, 4),
    (21, 9, 1, 22),
]
# Same as PROBLEM4 but with a small cube replacing a tile
PROBLEM4b = [
    (22, 1, 2, 4),
    (27, 9, 3, 0),
    (0, 3, 6, 5),
    (1, 8, 7, 2),
    (0, 5, 10, 22),
    (2, 6, 11, 4),
    (2, 7, 12, 5),
    (3, 8, 13, 6),
    (3, 9, 14, 7),
    (1, 26, 15, 8),
    (4, 11, 18, 20),
    (5, 12, 16, 10),
    (6, 13, 16, 11),
    (7, 14, 17, 12),
    (8, 15, 17, 13),
    (9, 21, 19, 14),
    (12, 17, 18, 11),
    (13, 14, 19, 16),
    (16, 19, 20, 10),
    (17, 15, 21, 18),
    (18, 21, 22, 10),
    (19, 15, 23, 20),
    (20, 24, 0, 4),
    #  (21, 9, 1, 22),
    (21, 26, 25, 24),
    (23, 25, 27, 22),
    (23, 26, 27, 24),
    (23, 9, 27, 25),
    (25, 26, 1, 24),

]
#             00
#          01 02 03
#             04
#    05       10       15
# 06 07 08 11 12 13 16 17 18
#    09       14       19
#             20
#          21 22 23
#             24
#             25
PROBLEM5 = [
    (25, 3, 2, 1),
    (0, 2, 4, 5),
    (0, 3, 4, 1),
    (0, 15, 4, 2),
    (2, 3, 10, 1),
    (1, 8, 7, 6),
    (5, 7, 9, 25),
    (5, 8, 9, 6),
    (5, 11, 9, 7),
    (7, 8, 21, 6),
    (4, 13, 12, 11),
    (10, 12, 14, 8),
    (10, 13, 14, 11),
    (10, 16, 14, 12),
    (12, 13, 20, 11),
    (3, 18, 17, 16),
    (15, 17, 19, 13),
    (15, 18, 19, 16),
    (15, 25, 19, 17),
    (17, 18, 23, 16),
    (14, 23, 22, 21),
    (20, 22, 24, 9),
    (20, 23, 24, 21),
    (20, 19, 24, 22),
    (22, 23, 25, 21),
    (24, 18, 0, 6),
]
#
#                 00
#         +--- 01 02 03 ---+
#         |       04       |
#        05       10       15
#   +-06 07 08 11 12 13 16 17 18 -+
#   |    09       14       19     |
#   |    |        20       |      |
#   |    +---- 21 22 23----+      |
#   |             24              |
#   |             25              |
#   +--------  26 27 28-----------+
#                 29
PROBLEM6 = [
    (29, 3, 2, 1),
    (0, 2, 4, 5),
    (0, 3, 4, 1),
    (0, 15, 4, 2),
    (2, 3, 10, 1),
    (1, 8, 7, 6),
    (5, 7, 9, 26),
    (5, 8, 9, 6),
    (5, 11, 9, 7),
    (7, 8, 21, 6),
    (4, 13, 12, 11),
    (10, 12, 14, 8),
    (10, 13, 14, 11),
    (10, 16, 14, 12),
    (12, 13, 20, 11),
    (3, 18, 17, 16),
    (15, 17, 19, 13),
    (15, 18, 19, 16),
    (15, 28, 19, 17),
    (17, 18, 23, 16),
    (14, 23, 22, 21),
    (20, 22, 24, 9),
    (20, 23, 24, 21),
    (20, 19, 24, 22),
    (22, 23, 25, 21),
    (24, 28, 27, 26),
    (25, 27, 29, 6),
    (25, 28, 29, 26),
    (25, 18, 29, 27),
    (27, 28, 0, 26),
]

#
#                 00
#         +--- 01 02 03 ---+
#         |       04       |
#        05       10       |
#   +-06 07 08 11 12 13 -- 15 ----+
#   |    09       14       |      |
#   |    |        |        |      |
#   |    +------- 16 ------+      |
#   +-------------17 -------------+
#
PROBLEM7 = [
    (17, 3, 2, 1),
    (0, 2, 4, 5),
    (0, 3, 4, 1),
    (0, 15, 4, 2),
    (2, 3, 10, 1),
    (1, 8, 7, 6),
    (5, 7, 9, 17),
    (5, 8, 9, 6),
    (5, 11, 9, 7),
    (7, 8, 16, 6),
    (4, 13, 12, 11),
    (10, 12, 14, 8),
    (10, 13, 14, 11),
    (10, 15, 14, 12),
    (12, 13, 16, 11),
    (3, 17, 16, 13),
    (14, 15, 17, 9),
    (16, 15, 0, 6),
    (23, 21, 20, 19),
    (18, 20, 22, 23),
    (18, 21, 22, 19),
    (18, 23, 22, 20),
    (20, 21, 23, 19),
    (22, 21, 18, 19)
]

Orientations = ['ID', 'R1', 'R2', 'R3', 'F', 'R1F', 'R2F', 'R3F']


def get_cubits(tiles: list[tuple[int, int, int, int]]) -> list[int]:
    """
    There are 16 "cubits" around the edge of a tile, which are numbered from 0 to 15 starting at the NW
    corner and moving clockwise to the NE corner, then to the SE, SW and back toward the NW corner.
     0  1  2  3  4
    15     N     5
    14 W       E 6
    13     S     7
    12 11 10  9  8

    Cubits are shared between neighboring tiles. E.g., if Tile 0's South side borders Tile 1's East side,
    then Tile 0's cubits 8, 9, 10, 11, 12 are the same as Tile 1's cubits 8, 7, 6, 5, 4 respectively.

    This function returns a list res of length 16 * n, where n is the number of tiles of a problem, such that
    res[16 * i + j] == res[16 * k + m] if and only if Tile i's j'th cubit is the same as Tile k's m'th cubit.
    """
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

    for tile1, value in enumerate(tiles):
        for tile1_side, tile2 in enumerate(value):
            tile2_side = next(i for i, v in enumerate(tiles[tile2]) if v == tile1)
            for i in range(5):
                union(
                    16 * tile1 + (4 * tile1_side + i) % 16,
                    16 * tile2 + (4 * tile2_side + 4 - i) % 16,
                )
    for i in range(len(res)):
        find(i)
    return res


class Piece:

    def __init__(self, pattern: str, color: Optional[str] = None, index: int = None):
        self._color = color
        self._index = index
        self._orientation = "ID"
        m = [[int(c) for c in s] for s in pattern.splitlines()]
        self._edge = tuple(m[0][:-1] + [r[-1] for r in m[:-1]] + m[-1][-1:0:-1] + [r[0] for r in m[-1:0:-1]])

    @property
    def orientation(self):
        return self._orientation

    def set_orientation(self, orientation: str):
        self._orientation = orientation

    @property
    def edge(self):
        edge = self._edge
        match self._orientation:
            case "ID":
                return edge
            case "R1":
                return edge[12:] + edge[:12]
            case "R2":
                return edge[8:] + edge[:8]
            case "R3":
                return edge[4:] + edge[:4]
            case "F":
                return edge[4::-1] + edge[:4:-1]
            case "R1F":
                return edge[8::-1] + edge[:8:-1]
            case "R2F":
                return edge[12::-1] + edge[:12:-1]
            case "R3F":
                return edge[0::-1] + edge[:0:-1]

    @property
    def color(self):
        return self._color

    @property
    def index(self):
        return self._index

    def __str__(self):

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
            n = int(f'{m[i - 1][j - 1]}{m[i - 1][j]}{m[i][j - 1]}{m[i][j]}', 2)
            k = 3 * (n if n <= 7 else 15 ^ n)
            return '    ┌──┐ ─── └─ │ ─┼──┘ '[k:k + 3]

        return '\n'.join(''.join(c(i, j) for j in range(1, 7))[1:].rstrip() for i in range(1, 7))

    def corners(self) -> int:
        return sum(i for i in self._edge[0::4])

    def mid_cubits(self) -> int:
        return sum(i for i in self._edge[2::4])

    def other_cubits(self) -> int:
        return sum(i for i in self._edge[1::2])


class Pad2(Enum):
    BLUE = """
    01000
    01111
    11111
    01110
    00100

    00100
    11111
    01110
    11111
    01010

    11011
    01111
    01110
    11110
    10100

    10101
    11111
    01110
    11110
    11011

    01010
    11110
    01111
    11111
    00100
    
    10100
    11111
    11111
    01110
    00100
    """
    GREEN = """
    11010
    01110
    11111
    01110
    01010

    01011
    11110
    01111
    11110
    01010

    11011
    01110
    11111
    01110
    01010

    01011
    01111
    11110
    01111
    11010

    00100
    01110
    11111
    01110
    00100

    00100
    01111
    11110
    01111
    11011
    """
    PINK = """
    00100
    11111
    01110
    11111
    01010

    01100
    01111
    11110
    01111
    00100

    00011
    11110
    01111
    11110
    00100

    10101
    11111
    01110
    11111
    11000

    00100
    01110
    11111
    11110
    10100

    11011
    11111
    01110
    11111
    10100
    """
    PURPLE = """
    11000
    11111
    01110
    01111
    01010

    10101
    11111
    01110
    01110
    01100

    00111
    11111
    11110
    01110
    01010

    00100
    01111
    11111
    11110
    10100

    11001
    01111
    11110
    01111
    01010

    10100
    11110
    01111
    01111
    01100
    """
    RED = """
    11101
    01111
    11110
    01110
    00100

    01000
    11111
    01111
    11110
    01010

    01011
    01111
    11110
    01110
    01010

    10101
    11111
    01111
    11110
    11010

    00101
    01111
    11111
    11110
    00100

    00100
    01111
    01110
    11110
    11010
    """
    YELLOW = """
    11011
    01111
    11110
    01111
    00011

    00110
    01110
    11111
    01110
    01010

    00100
    11110
    01110
    11111
    00111

    11000
    11111
    01110
    01111
    11011

    00100
    11110
    01111
    11111
    11000

    00100
    11110
    11111
    01110
    01100
    """


class Pad(Enum):
    BLUE = """
    00100
    01110
    11111
    01110
    00100

    10101
    11111
    01110
    11111
    10101

    00100
    01111
    11110
    01111
    00100
    
    01010
    11110
    01111
    11110
    11011
    
    01010
    11111
    01110
    11111
    00101
    
    01010
    01111
    11110
    01111
    01011
    """
    ORANGE = """
    10101
    11111
    01110
    11110
    01010
    
    00100
    01110
    11111
    11111
    00100
    
    01011
    11110
    01111
    01110
    11011
    
    00100
    11111
    01110
    11111
    10101
    
    11010
    01111
    11110
    01111
    00110
    
    00100
    01110
    11110
    01111
    01010
    """
    PURPLE = """
    01010
    01110
    11110
    01111
    11011
    
    10110
    11110
    11111
    01111
    00101
    
    11010
    11110
    01111
    01110
    01011
    
    00100
    01111
    11110
    11110
    11010
    
    01010
    01110
    11111
    11110
    00011
    
    00100
    11110
    01111
    11110
    01000
    """
    RED = """
    10110
    11111
    01110
    11111
    11001
    
    01011
    01110
    11111
    01110
    00011
    
    01000
    11110
    01111
    11110
    01010
    
    00110
    01110
    11111
    01110
    11011
    
    01100
    11111
    01110
    11111
    00101
    
    00100
    01111
    11110
    01111
    00100
    """
    YELLOW = """
    11100
    01110
    11111
    01110
    01011
    
    01010
    01111
    01110
    11111
    10100
    
    00100
    11110
    01111
    11110
    01010
    
    10101
    11111
    01110
    11111
    10100
    
    00100
    01111
    11110
    01111
    11010
    
    01010
    01110
    11111
    01110
    01011
    """

    @cache
    def to_list(self):
        v = self.value.strip()
        lines = v.splitlines()
        return '\n'.join(line.strip(' ') for line in lines).split('\n\n')

    def __getitem__(self, item):
        return self.to_list()[item]


def filter_pieces(num_tiles: int, num_corners: int, pieces: Iterable[Piece]):
    for pcs in combinations(pieces, num_tiles):
        if (
                sum(pc.corners() for pc in pcs) == num_corners and
                sum(pc.mid_cubits() for pc in pcs) == 2 * num_tiles and
                sum(pc.other_cubits() for pc in pcs) == 4 * num_tiles
        ):
            yield pcs


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
            for tile, pc_color, pc_idx, orientation in self._hints:
                ignored_tiles.add(tile)
                ignored_pieces.add((pc_color, pc_idx))
                piece = Piece(Pad[pc_color][pc_idx], pc_color, pc_idx)
                piece.set_orientation(orientation)
                ignored_cubits |= {self._cubits[tile * 16 + i] for i, v in enumerate(piece.edge) if v == 1}
        tiles = [tile for tile in range(self._num_tiles) if tile not in ignored_tiles]
        pieces = [pc for pc in self._pieces if (pc.color, pc.index) not in ignored_pieces]
        cubits = set(self._cubits) - ignored_cubits
        cubit_map = {j: i for i, j in enumerate(cubits)}
        columns = [True] * len(cubits) + [False] * len(pieces)
        num_primary_cols = len(cubits)
        for tile in tiles:
            for i, piece in enumerate(pieces):
                for orientation in Orientations:
                    piece.set_orientation(orientation)
                    cubit_set = {self._cubits[tile * 16 + i] for i, v in enumerate(piece.edge) if v == 1}
                    if not cubit_set <= cubits:
                        continue
                    row = [0] * len(columns)
                    for cubit in cubit_set:
                        row[cubit_map[cubit]] = 1
                    row[num_primary_cols + i] = 1
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
    resused_piece = next((p for p, v in piece_assignment.items() if len(v) > 1), None)
    if resused_piece:
        print(f"Piece {resused_piece} is used more than once.")
        res = False
    cubits = get_cubits(tiles)
    covered_cubits = defaultdict(list)
    for tile, color, index, orientation in solution:
        if (color, index) not in pieces:
            print(f"The solution uses {(color, index)}, which is not in the pieces for this problem.")
            res = False
        try:
            piece = Piece(Pad[color][index], color, index)
            piece.set_orientation(orientation)
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
        pad_pieces: list[tuple[str, int]],
        hints: list[tuple[int, str, int, str]] = None,
):
    pieces = [Piece(Pad[color][index], color, index) for color, index in pad_pieces]
    problem = Problem(tiles, pieces, hints)
    return ([(tile, p.color, p.index, orientation) for tile, p, orientation in a] for a in problem.solve())


def main():
    # hints = [
    #     (0, "PURPLE", 4, "R2F"),
    #     (1, "PINK", 0, "R2"),
    #     (2, "YELLOW", 4, "R3"),
    #     (3, "YELLOW", 1, "R3"),
    #     (4, "GREEN", 1, "R3"),
    #     (5, "GREEN", 5, "F"),
    #     (6, "PINK", 2, "R2F"),
    #     (7, "GREEN", 0, "R1F"),
    #     (8, "PINK", 1, "R1F"),
    #     (9, "RED", 1, "R2"),
    #     (10, "GREEN", 4, "ID"),
    #     (11, "YELLOW", 0, "R1F"),
    #     (12, "RED", 2, "ID"),
    #     (13, "BLUE", 4, "F"),
    #     (14, "GREEN", 3, "R3F"),
    #     (15, "PINK", 4, "R1F"),
    #     (16, "PINK", 3, "R3"),
    #     (17, "PURPLE", 5, "R1"),
    #     (18, "PURPLE", 0, "R2"),
    #     (19, "YELLOW", 2, "R3"),
    #     (20, "BLUE", 1, "ID"),
    #     (21, "BLUE", 5, "R2"),
    #     (22, "PURPLE", 1, "ID"),
    #     (23, "BLUE", 0, "R2"),
    #     (24, "PURPLE", 2, "R1F"),
    #     (25, "YELLOW", 3, "ID"),
    #     (26, "YELLOW", 5, "R2"),
    #     (27, "RED", 5, "F"),
    #     (28, "PURPLE", 3, "F"),
    #     (29, "GREEN", 2, "R3"),
    # ]
    start = time.time()
    # a = next(solve(PROBLEM6, [(pad.name, i) for pad in Pad for i in range(6)], sample(hints, 6)))
    hints = [
        (0, "BLUE", 3, "R1"),
        (1, "BLUE", 4, "R1F"),
        (2, "PURPLE", 5, "R1"),
        (5, "RED", 4, "F"),
        (6, "ORANGE", 2, "F"),
        (22, 'RED', 5, 'R3'),
        (23, 'YELLOW', 1, 'F')
    ]
    a = next(solve(PROBLEM4, filter_pieces_for_problem_4()[57], hints))
    a.extend(hints)
    a.sort()
    print(', '.join(str(x) for x in a))
    for tile, color, index, orientation in a:
        print(f'{tile}: {color}[{index}]')
        p = Piece(Pad[color][index], color, index)
        p.set_orientation(orientation)
        print(p)
    end = time.time()
    print(f'Time = {int((end - start) * 1000)} ms')


def main2():
    start = time.time()
    a = next(solve(PROBLEM1x6, [(pad.name, i) for pad in Pad for i in range(6)]))
    for tile, p in a:
        print(f'{tile}: {p.color}[{p.index}]')
        print(p)
    end = time.time()
    print(f'Time = {int((end - start) * 1000)} ms')


def main3():
    start = time.time()
    print("=" * 20)
    pieces = [(pad.name, i) for pad in Pad for i in range(6)]
    a = next(solve(PROBLEM7, pieces))
    print(', '.join([f'({tile}, "{color}", {index}, "{orientation}")' for tile, color, index, orientation in a]))
    for tile, color, index, orientation in a:
        print(f'{tile}: {color}[{index}]')
        p = Piece(Pad[color][index], color, index)
        p.set_orientation(orientation)
        print(p)
    end = time.time()
    print(f'Time = {int((end - start) * 1000)} ms')


def filter_pieces_for_problem_4():
    pieces = [Piece(Pad[color][index], color, index)
              for pad in Pad
              for color, index in ((pad.name, i) for i in range(6))]
    return [[(pc.color, pc.index) for pc in pcs] for pcs in filter_pieces(24, 26, pieces)]


if __name__ == '__main__':
    main3()
