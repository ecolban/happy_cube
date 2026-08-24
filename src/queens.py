from time import perf_counter

import click
from rust_dlx_lib import DlxSolver


# from py_dlx_solver import DlxSolver


def create_matrix(n):
    matrix = []
    # There are n row constraints, n column constraints, 2 * n - 1 first diagonal constraints, and 2 * n - 1 second
    # diagonal constraints resulting in 6 * n - 2 columns
    offsets = (0, n, 2 * n, 4 * n - 1)
    num_columns = 6 * n - 2
    # Dummy rows for diagonal columns, which are secondary
    for c in range(offsets[2], num_columns):
        row = [1 if j == c else 0 for j in range(num_columns)]
        matrix.append(row)
    # For each placement of a queen in row r and column c, add a regular row
    for r in range(n):
        for c in range(n):
            row = [0] * num_columns
            for j in range(num_columns):
                row[offsets[0] + r] = 1  # row constraints
                row[offsets[1] + c] = 1  # column constraints
                row[offsets[2] + r + c] = 1  # first diagonal constraints
                row[offsets[3] + r - c + n - 1] = 1  # second diagonal constraint
            matrix.append(row)

    return matrix


def get_queens(solution, n):
    dummy_rows = 4 * n - 2  # number of dummy rows
    res = [0] * n
    for i in solution:
        if i >= dummy_rows:
            r, c = divmod(i - dummy_rows, n)
            res[r] = c
    return res


def rotate90(r, c, n) -> tuple[int, int]:
    return n - 1 - c, r


def rotate180(r, c, n) -> tuple[int, int]:
    return n - 1 - r, n - 1 - c


def rotate270(r, c, n) -> tuple[int, int]:
    return c, n - 1 - r


def flip_h(r, c, n) -> tuple[int, int]:
    return n - 1 - r, c


def flip_v(r, c, n) -> tuple[int, int]:
    return r, n - 1 - c


def flip_d1(r, c, n) -> tuple[int, int]:
    return c, r


def flip_d2(r, c, n) -> tuple[int, int]:
    return n - 1 - c, n - 1 - r


SYMMETRIES = [rotate90, rotate180, rotate270, flip_h, flip_v, flip_d1, flip_d2]


def get_symmetric(solution, f, n):
    res = [0] * n
    for r, c in enumerate(solution):
        i, j = f(r, c, n)
        res[i] = j
    return res


def solve(n):
    solver = DlxSolver(create_matrix(n), [])
    for solution in solver:
        queens = get_queens(solution, n)
        if not any(get_symmetric(queens, f, n) < queens for f in SYMMETRIES):
            symmetry_group = {tuple(queens)}
            for f in SYMMETRIES:
                symmetry_group.add(tuple(get_symmetric(queens, f, n)))
            yield queens, len(symmetry_group)


def print_grid(queens):
    n = len(queens)
    for c in queens:
        print(''.join('*' if j == c else '_' for j in range(n)))


def main(n):
    start = perf_counter()
    total_count = 0
    for queens, count in solve(n):
        total_count += count
        if count < 8:
            print('=' * 20)
            print_grid(queens)
    print(f"{total_count = }")
    print(f"Time = {perf_counter() - start: 0.4f} secs")


@click.command()
@click.argument('n', type=int)
def _main(n):
    main(n)


if __name__ == '__main__':
    _main()
