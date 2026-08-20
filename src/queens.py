from time import perf_counter

import click
from rust_dlx_lib import DlxSolver


def create_matrix(dim):
    matrix = []
    for r in range(dim):
        for c in range(dim):
            # dim row constraints, dim column constraints,
            # 2 * dim - 1 first diagonal constraints, 2 * dim - 1 second diagonal constraints
            offsets = (0, dim, 2 * dim, 4 * dim - 1)
            row1 = [0] * (6 * dim - 2)
            row1[offsets[0] + r] = 1  # row constraints
            row1[offsets[1] + c] = 1  # column constraints
            row1[offsets[2] + r + c] = 1  # first diagonal constraints
            row1[offsets[3] + r - c + dim - 1] = 1  # second diagonal constraint
            row = row1
            matrix.append(row)
    # dummy rows for secondary columns
    for c in range(2 * dim, 6 * dim - 2):
        row = [0] * (6 * dim - 2)
        row[c] = 1
        matrix.append(row)

    return matrix


def solve(dim):
    solver = DlxSolver(create_matrix(dim), [40])
    solution = next(solver)
    for n in solution:
        if n < dim ** 2:
            r, c = divmod(n, dim)
            yield r, c


def main(dim):
    start = perf_counter()
    grid = [['_'] * dim for _ in range(dim)]
    for r, c in solve(dim):
        grid[r][c] = '*'
    for r in range(dim):
        print(*grid[r])
    end = perf_counter()
    print(f"Solved in {end - start:.4f} seconds")


@click.command()
@click.argument('dim', type=int)
def _main(dim):
    main(dim)


if __name__ == '__main__':
    _main()
