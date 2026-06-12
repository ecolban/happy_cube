from collections.abc import Iterable
from itertools import groupby
from operator import itemgetter
from time import perf_counter

from exact_cover import ExactCover


def columns() -> Iterable[bool]:
    return (True for _ in range(324))


def rows() -> Iterable[list[int]]:
    offsets = [i * 81 for i in range(5)]

    def get_row(row, col, val):
        box = row - row % 3 + col // 3
        res = [0] * offsets[4]
        res[offsets[0] + row * 9 + col] = 1
        res[offsets[1] + row * 9 + val] = 1
        res[offsets[2] + col * 9 + val] = 1
        res[offsets[3] + box * 9 + val] = 1
        return res

    return (get_row(r, c, v) for r in range(9) for c in range(9) for v in range(9))


def row_idx(row: int, col: int, val: int) -> int:
    return (row * 9 + col) * 9 + val - 1


def row_col_val(i: int) -> tuple[int, int, int]:
    i, val = divmod(i, 9)
    row, col = divmod(i, 9)
    return row, col, val + 1


def solve(grid: list[list[int]]) -> list[list[int]]:
    clues = [row_idx(r, c, v) for r, row in enumerate(grid) for c, v in enumerate(row) if v]
    exact_cover = ExactCover(columns=columns(), rows=rows(), clues=clues)
    sol = next(exact_cover.solve())
    return [[v for _, _, v in g] for _, g in groupby(
        sorted((row_col_val(i) for i in sol)),
        key=itemgetter(0),
    )]


if __name__ == '__main__':

    def main(problem: list[list[int]]) -> None:
        start = perf_counter()
        solution = solve(problem)
        print(f"Time: {int((perf_counter() - start) * 1000 + 0.5)} ms")
        for row in solution:
            print(*row)


    main([
        [0, 9, 0, 0, 0, 0, 5, 7, 0],
        [4, 0, 0, 0, 6, 0, 0, 8, 0],
        [0, 0, 0, 0, 0, 7, 0, 0, 4],
        [8, 0, 1, 0, 0, 3, 0, 0, 6],
        [0, 2, 0, 9, 7, 0, 0, 5, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 4, 0, 0, 2, 0, 0, 0, 0],
        [3, 0, 0, 0, 0, 6, 0, 0, 2],
        [0, 0, 0, 0, 9, 0, 0, 0, 0],
    ])
