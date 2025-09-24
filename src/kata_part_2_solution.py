from collections.abc import Iterable
from enum import Enum, auto
from functools import cache
from itertools import chain

from preloaded import Pads


class Orientations(Enum):
    R0 = auto()
    R1 = auto()
    R2 = auto()
    R3 = auto()
    F0 = auto()
    F1 = auto()
    F2 = auto()
    F3 = auto()


class Piece:
    def __init__(self, color: str, index: int, orientation: str = Orientations.R0.name):
        self._color = color
        self._index = index
        self._orientation = Orientations[orientation]
        self._edge: list[int] = list(get_edge(Pads[color], index))

    @property
    def edge(self):
        @cache
        def _edge(orientation: Orientations):
            edge = self._edge
            match orientation:
                case Orientations.R0:
                    return edge
                case Orientations.R1:
                    return [edge[(12 + i) % 16] for i in range(16)]
                case Orientations.R2:
                    return [edge[(8 + i) % 16] for i in range(16)]
                case Orientations.R3:
                    return [edge[(4 + i) % 16] for i in range(16)]
                case Orientations.F0:
                    return [edge[(4 - i) % 16] for i in range(16)]
                case Orientations.F1:
                    return [edge[(8 - i) % 16] for i in range(16)]
                case Orientations.F2:
                    return [edge[(12 - i) % 16] for i in range(16)]
                case Orientations.F3:
                    return [edge[(-i) % 16] for i in range(16)]

        return _edge(self._orientation)


def get_edge(pad: Pads, index: int) -> Iterable[int]:
    """Returns the edge of the piece with given index of given pad"""
    c = str(index)
    lines = pad.value.splitlines()
    row_min = next(i for i, row in enumerate(lines) if c in row)
    row_max = row_min + 4
    col_min = 100
    for i, row in enumerate(lines[row_min: row_max + 1], start=row_min):
        col_start = next(j for j, v in enumerate(row) if v == c)
        col_min = min(col_min, col_start)
    col_max = col_min + 4
    return chain(
        (int(lines[row_min][i] == c) for i in range(col_min, col_max)),
        (int(lines[i][col_max] == c) for i in range(row_min, row_max)),
        (int(lines[row_max][i] == c) for i in range(col_max, col_min, -1)),
        (int(lines[i][col_min] == c) for i in range(row_max, row_min, -1)),
    )


def get_covered_shape_slots(
        tile: int,
        color: str,
        index: int,
        orientation: str,
        slot_map: list[int],
) -> list[int]:
    piece = Piece(color, index, orientation)
    return sorted(slot_map[16 * tile + i] for i, v in enumerate(piece.edge) if v)
