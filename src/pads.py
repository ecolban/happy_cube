from enum import Enum

import preloaded


class Pads(Enum):
    BLUE = preloaded.Pads.BLUE.value
    GREEN = preloaded.Pads.GREEN.value
    PINK = preloaded.Pads.PINK.value
    PURPLE = preloaded.Pads.PURPLE.value
    RED = preloaded.Pads.RED.value
    YELLOW = preloaded.Pads.YELLOW.value

    def _matrix(self):
        return list(filter(None, (list(line.strip()) for line in self.value.splitlines())))

    def __len__(self):
        return 7

    def __getitem__(self, item):
        """Returns the edge of the piece corresponding to item"""
        c = str(item)
        col_min, col_max = 100, -100
        row_min, row_max = 100, -100
        matrix = self._matrix()
        for i, row in enumerate(matrix):
            if c not in row:
                continue
            row_min = min(row_min, i)
            row_max = max(row_max, i)
            for j, k in enumerate(row):
                if k == c:
                    col_min = min(col_min, j)
                    col_max = max(col_max, j)
        return (
                [1 if matrix[row_min][i] == c else 0 for i in range(col_min, col_max)] +
                [1 if matrix[i][col_max] == c else 0 for i in range(row_min, row_max)] +
                [1 if matrix[row_max][i] == c else 0 for i in range(col_max, col_min, -1)] +
                [1 if matrix[i][col_min] == c else 0 for i in range(row_max, row_min, -1)]
        )

    def __iter__(self):
        return (self[i] for i in range(7))

    def __str__(self):
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

        def symbol(i, j):
            mp, n, idx = {}, 0, 0
            for k in (matrix_w_border[i + di][j + dj] for di in (0, 1) for dj in (0, 1)):
                if k not in mp:
                    mp[k] = n
                    n += 1
                idx = idx * 4 + mp[k]
            return symbols[idx]

        return '\n'.join(''.join(symbol(i, j) for j in range(w + 1)) for i in range(h + 1))


if __name__ == '__main__':
    for pad in Pads:
        print(pad.name)
        print(Pads(pad))
