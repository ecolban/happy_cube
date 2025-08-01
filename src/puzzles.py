from collections.abc import Generator
from enum import Enum
from itertools import combinations
from random import shuffle

from pieces import Piece


class Shapes(Enum):
    #  0
    # 123
    #  4
    #  5
    SHAPE1 = [
        (5, 3, 2, 1),
        (0, 2, 4, 5),
        (0, 3, 4, 1),
        (0, 5, 4, 2),
        (2, 3, 5, 1),
        (4, 3, 0, 1),
    ]
    SHAPE1x6 = [
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
    SHAPE2 = [
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
    SHAPE3 = [
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
    SHAPE4 = [
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
    # Same as SHAPE4 but with a small cube replacing a tile
    SHAPE4b = [
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
    SHAPE5 = [
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
    SHAPE6 = [
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
    SHAPE7 = [
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

    SHAPE8 = [
        (17, 3, 2, 1),
        (0, 2, 9, 14),
        (0, 4, 8, 1),
        (0, 6, 5, 4),
        (3, 5, 7, 2),  # 4
        (3, 6, 7, 4),
        (3, 16, 7, 5),
        (5, 6, 11, 4),
        (2, 11, 10, 9),
        (8, 10, 12, 1),  # 9
        (8, 11, 12, 9),
        (8, 7, 12, 10),
        (10, 11, 13, 9),
        (12, 16, 15, 14),
        (13, 15, 17, 1),  # 14
        (13, 16, 17, 14),
        (13, 6, 17, 15),
        (15, 16, 0, 14),
    ]

    @property
    def tiles(self):
        return self.value


def filter_pieces(tiles, pieces: list[Piece]) -> Generator[list[Piece], None, None]:
    cubits = get_cubits(tiles)
    num_tiles = len(tiles)
    corners = {cubits[tile * 16 + i] for tile in range(num_tiles) for i in range(0, 16, 4)}
    num_corners = len(corners)
    for pcs in combinations(pieces, num_tiles):
        if (
                sum(pc.corners() for pc in pcs) == num_corners and
                sum(pc.mid_cubits() for pc in pcs) == 2 * num_tiles and
                sum(pc.other_cubits() for pc in pcs) == 4 * num_tiles
        ):
            yield pcs


def shape_shuffle(tiles: list[tuple[int, int, int, int]]) -> list[tuple[int, int, int, int]]:
    num_tiles = len(tiles)
    permutation = list(range(num_tiles))
    shuffle(permutation)
    res = {}
    for i, v in enumerate(tiles):
        res[permutation[i]] = tuple(permutation[j] for j in v)
    # noinspection PyTypeChecker
    return [res[i] for i in range(num_tiles)]


def get_cubits(tiles) -> list[int]:
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
