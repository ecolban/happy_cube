from collections import defaultdict
from enum import Enum
from itertools import chain

from kata_part_3_solution import PieceSpec, SolutionSpec
from pads import PadsBase


def check_solution(
    shape: list[tuple[int, int, int, int]],
    pieces: set[PieceSpec],
    hints: list[tuple[int, str, int, str]] | None,
    solution: SolutionSpec,
    tack_stitches: list[tuple[int, int]] | None = None,
) -> list[str]:
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
            self._direction = direction
            self._offset = offset
            self._indexes = [(offset + direction * i) % 16 for i in range(16)]

        def apply_to(self, edge: list[int]):
            return (edge[i] for i in self._indexes)

        def rotate(self, k):
            sign = self._direction
            return Orientations((sign, (self._offset - sign * k * 4) % 16))

    def get_edge(pad_: PadsBase, index_: int, orientation_str_: str) -> list[int]:
        """Returns the edge of the piece with given index of given pad"""
        c = str(index_)
        lines = pad_.value.splitlines()
        row_min = next(i for i, row in enumerate(lines) if c in row)
        row_max = row_min + 4
        col_min = 100
        for i, row in enumerate(lines[row_min: row_max + 1], start=row_min):
            col_start = next(j for j, v in enumerate(row) if v == c)
            col_min = min(col_min, col_start)
        col_max = col_min + 4
        edge = list(chain(
            (int(lines[row_min][i] == c) for i in range(col_min, col_max)),
            (int(lines[i][col_max] == c) for i in range(row_min, row_max)),
            (int(lines[row_max][i] == c) for i in range(col_max, col_min, -1)),
            (int(lines[i][col_min] == c) for i in range(row_max, row_min, -1)),
        ))
        return list(Orientations[orientation_str_].apply_to(edge))

    def get_shape_slots() -> list[int]:
        num_tiles = len(shape)
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

        for tile1, neighbors in enumerate(shape):
            for edge1, tile2 in enumerate(neighbors):
                if tile2 > tile1:
                    edge2 = next(i for i, v in enumerate(shape[tile2]) if v == tile1)
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

    errors = []
    covered_tiles = set(tile for tile, *_ in solution)
    uncovered_tiles = set(range(len(shape))) - covered_tiles
    for uncovered_tile in uncovered_tiles:
        errors.append(f"No piece has been assigned to tile {uncovered_tile}.")
    piece_assignment = defaultdict(list)
    for tile, pad, index, _ in solution:
        piece_assignment[(pad, index)].append(tile)
    reused_pieces = (p for p, v in piece_assignment.items() if len(v) > 1)
    for reused_piece in reused_pieces:
        errors.append(f"Piece {reused_piece} is used more than once.")
    slots = get_shape_slots()
    covered_slots = defaultdict(list)
    for tile, pad, index, orientation_str in solution:
        if (pad, index) not in pieces:
            errors.append(f"The solution uses {(pad, index)}, which is not in the pieces for this problem.")
        try:
            edge = get_edge(pad, index, orientation_str)
            for i, v in enumerate(edge):
                if v == 1:
                    covered_slots[slots[16 * tile + i]].append((pad, index, tile))
        except (IndexError, KeyError) as e:
            errors.append(e)
    uncovered_slots = (slot for slot in set(slots) if not covered_slots[slot])
    for uncovered_slot in uncovered_slots:
        tile, i = divmod(uncovered_slot, 16)
        errors.append(f"Slot {i} of tile {tile} is not covered by any piece.")
    collision_slots = (slot for slot, v in covered_slots.items() if len(v) > 1)
    for slot in collision_slots:
        a = ' and '.join(
            f"piece {(color, index)} assigned to tile {tile}" for color, index, tile in covered_slots[slot])
        tile, i = divmod(slot, 16)
        errors.append(f"Slot {i} of tile {tile} is covered by {a}")

    if hints and not set(hints) <= set(solution):
        errors.append("The solution is not an extension of the hints")
    return errors
