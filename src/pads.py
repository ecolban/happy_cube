from collections.abc import Iterator
from enum import StrEnum


class PadsBase(StrEnum):
    """Base class for Pads enums with shared methods"""

    def label(self) -> str:
        return f"{type(self).__name__}.{self.name}"

    def __repr__(self) -> str:
        return self.label()

    def __format__(self, format_spec: str) -> str:
        return format(self.label(), format_spec)

    def _matrix(self) -> list[list[str]]:
        return list(filter(None, (list(line.strip()) for line in self.value.splitlines())))

    def __len__(self) -> int:
        return 7

    def __getitem__(self, n: int) -> list[int]:
        """Returns the edge of the pad's nth piece"""
        if not 1 <= n <= 6:
            raise IndexError
        c = str(n)
        matrix = self._matrix()
        row_min = next(i for i, row in enumerate(matrix) if c in row)
        row_max = row_min + 4
        col_min = min(j for row in matrix[row_min: row_max + 1] for j, c_ in enumerate(row) if c_ == c)
        col_max = col_min + 4
        return (
            [1 if matrix[row_min][i] == c else 0 for i in range(col_min, col_max)] +
            [1 if matrix[i][col_max] == c else 0 for i in range(row_min, row_max)] +
            [1 if matrix[row_max][i] == c else 0 for i in range(col_max, col_min, -1)] +
            [1 if matrix[i][col_min] == c else 0 for i in range(row_max, row_min, -1)]
        )

    def __iter__(self) -> Iterator[list[int]]:
        return (self[i] for i in range(7))

    def __str__(self) -> str:
        symbols = {
            0: '   ',
            1: ' ┌─',
            4: '─┐ ',
            5: '───',
            6: '─┬─',
            16: ' └─',
            17: ' │ ',
            18: ' ├─',
            21: '─┘ ',
            25: '─┤ ',
            26: '─┴─',
            27: '─┼─',
        }
        matrix = self._matrix()
        w, h = len(matrix[0]), len(matrix)
        matrix_w_border = [
            ['1'] * (w + 2),
            *(['1', *line, '1'] for line in matrix),
            ['1'] * (w + 2)
        ]

        def symbol(i: int, j: int) -> str:
            mp, n, idx = {}, 0, 0
            for k in (matrix_w_border[i + di][j + dj] for di in (0, 1) for dj in (0, 1)):
                if k not in mp:
                    mp[k] = n
                    n += 1
                idx = idx * 4 + mp[k]
            return symbols[idx]

        return '\n'.join(''.join(symbol(i, j) for j in range(w + 1)) for i in range(h + 1))


class PadsSkatoy(PadsBase):
    BLUE = """
    000000000000000
    000102020203000
    011112222233300
    001111222333330
    011112222233300
    004142525263600
    044445555566660
    004444555666600
    044445555566660
    044044050560660
    000000000000000
    """
    ORANGE = """
    000000000000000
    010101020030330
    011111222333300
    001112222233330
    011112222233300
    001415525336330
    044444555566600
    004445555666600
    044444555566660
    040404055060600
    000000000000000
    """
    PURPLE = """
    000000000000000
    011010002230000
    011112222333300
    011112222233330
    001111222333300
    044144252563660
    004444555566600
    044445555566660
    004445555666600
    004045055660600
    000000000000000
    """
    RED = """
    000000000000000
    011011020203000
    001112222233330
    011111222333300
    001112222233330
    044114225663600
    044444555566600
    004445555666660
    044444555566600
    040440505660000
    000000000000000
    """
    YELLOW = """
    000000000000000
    010101202030330
    011111222233300
    001112222333330
    011111222233300
    014144525636300
    044445555666660
    004444555666600
    044445555566660
    000400050506060
    000000000000000
    """


class PadsDublin(PadsBase):
    BLUE = """
    000000000000000
    000101020030300
    001111222333300
    001112222233330
    011112222333330
    011411552663660
    044444555666600
    004445555566600
    044444555666660
    004045550606060
    000000000000000
    """
    GREEN = """
    000000000000000
    000100020330330
    011111222333300
    001112222233330
    011111222333300
    004141525663600
    004445555666600
    044444555566660
    004445555666600
    044044505560660
    000000000000000
    """
    PINK = """
    000000000000000
    001012202203000
    011112222233300
    001111222333330
    011112222233300
    001412525663330
    004444555666660
    044444555566600
    004445555666660
    004045050606060
    000000000000000
    """
    PURPLE = """
    000000000000000
    010102200330030
    011112222233330
    011111222333300
    001111222233330
    004145252536360
    004445555566660
    004444555666600
    044444555666600
    044400550006600
    000000000000000
    """
    RED = """
    000000000000000
    011000022303000
    001112222333300
    011111222333330
    011112222233330
    014145252563660
    004445555566660
    004444555566600
    044445555666600
    044045505006000
    000000000000000
    """
    YELLOW = """
    000000000000000
    001011022330000
    001111222333300
    001112222333330
    011111222233300
    011441252236360
    044445555566660
    044444555566600
    004445555666660
    000400050660660
    000000000000000
    """


if __name__ == '__main__':
    for pad in PadsSkatoy:
        print(pad.name)
        print(PadsSkatoy(pad))
