from collections import defaultdict
from collections.abc import Generator, Iterable
from enum import Enum
from itertools import combinations
from random import shuffle, randrange

from pads import Pads
from pieces import Piece, Orientations


class Shapes(Enum):
    #  0
    # 123
    #  4
    #  5
    CUBE_1x1x1 = [
        (5, 3, 2, 1),
        (0, 2, 4, 5),
        (0, 3, 4, 1),
        (0, 5, 4, 2),
        (2, 3, 5, 1),
        (4, 3, 0, 1),
    ]
    TWO_CUBE_1x1x1 = [
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
    ]
    SIX_CUBE_1x1x1 = [
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

        (29, 27, 26, 25),
        (24, 26, 28, 29),
        (24, 27, 28, 25),
        (24, 29, 28, 26),
        (26, 27, 29, 25),
        (28, 27, 24, 25),

        (35, 33, 32, 31),
        (30, 32, 34, 35),
        (30, 33, 34, 31),
        (30, 35, 34, 32),
        (32, 33, 35, 31),
        (34, 33, 30, 31),
    ]
    #  01
    # 2345
    #  67
    #  89
    PRISM_1x1x2 = [
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
    #    0  1  2
    # 3  4  5  6 7
    #    8  9 10
    #   11 12 13
    PRISM_1x1x3 = [
        (11, 1, 4, 3),
        (12, 2, 5, 0),
        (13, 7, 6, 1),
        (0, 4, 8, 11),
        (0, 5, 8, 3),
        (1, 6, 9, 4),
        (2, 7, 10, 5),
        (2, 13, 10, 6),
        (4, 9, 11, 3),
        (5, 10, 12, 8),
        (6, 7, 13, 9),
        (8, 12, 0, 3),
        (9, 13, 1, 11),
        (10, 7, 2, 12),
    ]
    #        0  1
    #        2  3
    #  4  5  6  7  8  9
    # 10 11 12 13 14 15
    #       16 17
    #       18 19
    #       20 21
    #       22 23
    CUBE_2x2x2 = [
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
    # Same as CUBE_2x2x2 but with a small cube replacing a tile
    CUBE_2x2x2_WITH_CUBE_1x1x1_OUTGROWTH = [
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
    CUBE_1x1x1_WITH_FIVE_CUBE_1x1x1_OUTGROWTHS = [
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
    THREE_D_CROSS = [
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
    CUBE_1x1x1_WITH_THREE_CUBE_1x1x1_OUTGROWTHS = [
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

    L_SHAPE = [
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
        (10, 16, 15, 14),
        (13, 15, 17, 12),
        (13, 16, 17, 14),
        (13, 7, 17, 15),
        (15, 16, 2, 14),
    ]

    C_SHAPE = [
        (21, 1, 4, 3),
        (12, 2, 5, 0),
        (17, 7, 6, 1),
        (0, 4, 8, 18),
        (0, 5, 8, 3),
        (1, 6, 9, 4),
        (2, 7, 10, 5),
        (2, 16, 10, 6),
        (4, 9, 11, 3),
        (5, 10, 12, 8),
        (6, 7, 13, 9),
        (8, 20, 19, 18),
        (9, 14, 1, 20),
        (10, 16, 15, 14),
        (13, 15, 17, 12),
        (13, 16, 17, 14),
        (13, 7, 17, 15),
        (15, 16, 2, 14),
        (11, 19, 21, 3),
        (11, 20, 21, 18),
        (11, 12, 21, 19),
        (19, 20, 0, 18),
    ]

    #      AA 01
    #   02 03 04 05
    #      06 BB
    #      08 09
    #
    # AA = 10
    #   11 00 12
    #      13
    #
    # BB = 14
    #   15 07 16
    #      17
    LIGHTNING_BOLT = [
        (10, 12, 13, 11),
        (9, 5, 4, 12),
        (11, 3, 6, 8),
        (13, 4, 6, 2),
        (1, 5, 14, 3),
        (1, 9, 16, 4),  # 5
        (3, 15, 8, 2),
        (14, 16, 17, 15),
        (6, 9, 10, 2),
        (17, 5, 1, 8),
        (8, 12, 0, 11),  # 10
        (10, 0, 13, 2),
        (10, 1, 13, 0),
        (0, 12, 3, 11),
        (4, 16, 7, 15),
        (14, 7, 17, 6),  # 15
        (14, 5, 17, 7),
        (7, 16, 9, 15)
    ]

    #      AA 01
    #   02 03 04 05
    #      06 BB
    #      08 09
    #
    # AA = 10
    #   CC 00 12
    #      13
    #
    # BB = 14
    #   15 07 16
    #      17
    #
    # CC = 18
    #   19 11 20
    #      21
    #
    W_SHAPE = [
        (10, 12, 13, 20),
        (9, 5, 4, 12),
        (19, 3, 6, 8),
        (13, 4, 6, 2),
        (1, 5, 14, 3),
        (1, 9, 16, 4),  # 5
        (3, 15, 8, 2),
        (14, 16, 17, 15),
        (6, 9, 10, 2),
        (17, 5, 1, 8),
        (8, 12, 0, 18),  # 10
        (18, 20, 21, 19),
        (10, 1, 13, 0),
        (0, 12, 3, 21),
        (4, 16, 7, 15),
        (14, 7, 17, 6),  # 15
        (14, 5, 17, 7),
        (7, 16, 9, 15),
        (10, 20, 11, 19),
        (18, 11, 21, 2),
        (18, 0, 21, 11),  # 20
        (11, 20, 13, 19),
    ]

    """2D cross"""
    TWO_D_CROSS = [
        (21, 3, 2, 1),
        (0, 2, 4, 5),
        (0, 3, 4, 1),
        (0, 11, 4, 2),
        (2, 3, 10, 1),
        (1, 8, 7, 6),
        (5, 7, 9, 21),
        (5, 8, 9, 6),
        (5, 10, 9, 7),
        (7, 8, 17, 6),
        (4, 12, 16, 8),
        (3, 14, 13, 12),
        (11, 13, 15, 10),
        (11, 14, 15, 12),
        (11, 21, 15, 13),
        (13, 14, 19, 12),
        (10, 19, 18, 17),
        (16, 18, 20, 9),
        (16, 19, 20, 17),
        (16, 15, 20, 18),
        (18, 19, 21, 17),
        (20, 14, 0, 6)
    ]

    CUBE_2x2x2_WITH_TWO_INVERTED_VERTICES = [
        (22, 1, 2, 4),  # 0
        (23, 9, 3, 0),
        (0, 7, 6, 5),
        (1, 9, 8, 7),
        (0, 5, 10, 22),
        (2, 6, 11, 4),  # 5
        (2, 7, 12, 5),
        (2, 3, 8, 6),
        (7, 3, 14, 13),
        (1, 23, 15, 3),
        (4, 18, 20, 22),  # 10
        (5, 12, 16, 18),
        (6, 13, 16, 11),
        (8, 14, 17, 12),
        (8, 15, 17, 13),
        (9, 21, 19, 14),  # 15
        (12, 17, 18, 11),
        (13, 14, 19, 16),
        (16, 20, 10, 11),
        (17, 15, 21, 20),
        (19, 21, 10, 18),  # 20
        (19, 15, 23, 20),
        (10, 23, 0, 4),
        (21, 9, 1, 22),
    ]

    @property
    def tiles(self):
        return self.value


def filter_pieces(
        shape: list[tuple[int, int, int, int]],
        pieces: list[tuple[str, int]],
        hints: list[tuple[int, str, int, str]] = None,
) -> Generator[list[tuple[str, int]], None, None]:
    piece_map = {(color, index): (pc.corners(), pc.mid_cubits(), pc.other_cubits())
                 for color, index in pieces for pc in (Piece(color, index),)}
    hints = hints or []
    for _, color, index, _ in hints:
        pieces.remove((color, index))
    hints_cubits = tuple(sum(piece_map[(color, index)][i] for _, color, index, _ in hints) for i in range(3))
    slots = get_shape_slots(shape)
    num_tiles = len(shape)
    corners = {slots[tile * 16 + i] for tile in range(num_tiles) for i in range(0, 16, 4)}
    num_corners = len(corners)
    for pcs in combinations(pieces, num_tiles - len(hints)):
        if (
                sum(piece_map[pc][0] for pc in pcs) + hints_cubits[0] == num_corners and
                sum(piece_map[pc][1] for pc in pcs) + hints_cubits[1] == 2 * num_tiles and
                sum(piece_map[pc][2] for pc in pcs) + hints_cubits[2] == 4 * num_tiles
        ):
            yield pcs


def shape_shuffle(tiles: list[tuple[int, int, int, int]]) -> list[tuple[int, int, int, int]]:
    num_tiles = len(tiles)
    permutation = list(range(num_tiles))
    shuffle(permutation)
    res = {}
    for i, v in enumerate(tiles):
        res[permutation[i]] = tuple(permutation[j] for j in v)
    for i, v in res.items():
        k = randrange(4)
        if k > 0:
            res[i] = tuple(v[(j + k) % 4] for j in range(4))
    # noinspection PyTypeChecker
    return [res[i] for i in range(num_tiles)]


def get_shape_slots(tiles) -> list[int]:
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

    for tile1, neighbors in enumerate(tiles):
        for edge1, tile2 in enumerate(neighbors):
            if tile2 > tile1:
                try:
                    edge2 = next(i for i, v in enumerate(tiles[tile2]) if v == tile1)
                except:
                    pass
                for i in range(5):
                    slot1 = 16 * tile1 + (4 * edge1 + i) % 16
                    slot2 = 16 * tile2 + (4 * edge2 + 4 - i) % 16
                    union(slot1, slot2)
    union(60, 164)
    for i in range(len(res)):
        find(i)
    return res


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
    cubits = get_shape_slots(tiles)
    covered_cubits = defaultdict(list)
    for tile, color, index, orientation in solution:
        if (color, index) not in pieces:
            print(f"The solution uses {(color, index)}, which is not in the pieces for this problem.")
            res = False
        try:
            piece = Piece(color, index)
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


SHAPE6_SOLUTION = [  # Uses Pads2
    (0, "PURPLE", 4, "F3"),
    (1, "PINK", 0, "R2"),
    (2, "YELLOW", 4, "R3"),
    (3, "YELLOW", 1, "R3"),
    (4, "GREEN", 1, "R3"),
    (5, "GREEN", 5, "F1"),
    (6, "PINK", 2, "F3"),
    (7, "GREEN", 0, "F2"),
    (8, "PINK", 1, "F2"),
    (9, "RED", 1, "R2"),
    (10, "GREEN", 4, "ID"),
    (11, "YELLOW", 0, "F2"),
    (12, "RED", 2, "ID"),
    (13, "BLUE", 4, "F1"),
    (14, "GREEN", 3, "F4"),
    (15, "PINK", 4, "F2"),
    (16, "PINK", 3, "R3"),
    (17, "PURPLE", 5, "R1"),
    (18, "PURPLE", 0, "R2"),
    (19, "YELLOW", 2, "R3"),
    (20, "BLUE", 1, "ID"),
    (21, "BLUE", 5, "R2"),
    (22, "PURPLE", 1, "ID"),
    (23, "BLUE", 0, "R2"),
    (24, "PURPLE", 2, "F2"),
    (25, "YELLOW", 3, "ID"),
    (26, "YELLOW", 5, "R2"),
    (27, "RED", 5, "F1"),
    (28, "PURPLE", 3, "F1"),
    (29, "GREEN", 2, "R3"),
]
