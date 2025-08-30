from enum import Enum, auto

from pads import Pads


class Orientations(str, Enum):
    ID = auto()
    R1 = auto()
    R2 = auto()
    R3 = auto()
    F1 = auto()
    F2 = auto()
    F3 = auto()
    F4 = auto()

    def __str__(self):
        return self.name


class Piece:

    def __init__(self, color: str, index: int):
        self._color = color
        self._index = index
        self._orientation = Orientations.ID
        pad = Pads[color].parse()[index]
        m = [[int(c) for c in s] for s in pad.splitlines()]
        self._edge = tuple(m[0][:-1] + [r[-1] for r in m[:-1]] + m[-1][-1:0:-1] + [r[0] for r in m[-1:0:-1]])

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
            case Orientations.ID:
                return edge
            case Orientations.R1:
                return edge[12:] + edge[:12]
            case Orientations.R2:
                return edge[8:] + edge[:8]
            case Orientations.R3:
                return edge[4:] + edge[:4]
            case Orientations.F1:
                return edge[4::-1] + edge[:4:-1]
            case Orientations.F2:
                return edge[8::-1] + edge[:8:-1]
            case Orientations.F3:
                return edge[12::-1] + edge[:12:-1]
            case Orientations.F4:
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
