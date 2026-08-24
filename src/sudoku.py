from collections.abc import Generator
from heapq import nsmallest
from random import shuffle, choice
from time import perf_counter

import click
# from py_dlx_solver import DlxSolver
from rust_dlx_lib import DlxSolver


def solve_sudoku(clues=None):
    """
    Solve a 9x9 Sudoku puzzle using DLX.
    grid: 9x9 list of lists (0 = empty, 1-9 = given digit).
    Returns a solved 9x9 grid, or None if unsolvable.
    """

    # 324 primary constraints
    def create_matrix() -> list[list[int]]:
        offsets = [i * 9 * 9 for i in range(4)]
        num_cols = 4 * 9 * 9

        def make_row(row, col, val):  # val is 0-based
            box = row - row % 3 + col // 3
            res = [0] * num_cols
            res[offsets[0] + row * 9 + col] = 1  # cell constraint
            res[offsets[1] + row * 9 + val] = 1  # row constraint
            res[offsets[2] + col * 9 + val] = 1  # column constraint
            res[offsets[3] + box * 9 + val] = 1  # box constraint
            return res

        # 9 * 9 * 9 candidate placements; index = r * 9 * 9 + c * 9 + d  (d is 0-based)
        return [make_row(r, c, d) for r in range(9) for c in range(9) for d in range(9)]

    rows = create_matrix()

    solutions = DlxSolver(rows, clues)
    return solutions


def row_idx(r, c, d):
    """The index of the row representing the placement of d to grid row r and grid column c."""
    return ((r * 9) + c) * 9 + (d - 1)


def row_idx_inv(i: int) -> tuple[int, int, int]:
    """The inverse of row_idx."""
    i, d = divmod(i, 9)
    r, c = divmod(i, 9)
    return r, c, (d + 1)


def generate_sudoku():
    row = list(range(1, 10))
    shuffle(row)
    clues = [row_idx(0, c, d) for c, d in enumerate(row)]
    solutions = solve_sudoku(clues)
    first, second = next(solutions, None), next(solutions, None)
    while first is not None and second is not None:
        clue = choice(list(set(second) - set(first)))
        clues.append(clue)
        solutions = solve_sudoku(clues)
        first, second = next(solutions, None), next(solutions, None)
    shuffle(clues)
    clue_idx = next((i for i in range(len(clues)) if has_unique_solution(remove(clues, i))), None)
    while clue_idx is not None:
        clues = remove(clues, clue_idx)
        clue_idx = next((i for i in range(clue_idx, len(clues)) if has_unique_solution(remove(clues, i))), None)
    return clues


def has_unique_solution(clues):
    solutions = solve_sudoku(clues)
    first_solution = next(solutions, None)
    second_solution = next(solutions, None)
    return first_solution is not None and second_solution is None


def remove(clues: list[int], idx: int) -> list[int]:
    return clues[:idx] + clues[idx + 1:]


def make_grid(clues: list[int]) -> str:
    grid = [[0 for _ in range(9)] for _ in range(9)]

    def gen_grid_line(row):
        for c, col in enumerate(row):
            if c % 3 == 0:
                yield '|'
            yield f' {col} ' if col > 0 else '   '
        yield '|'

    def gen_grid_lines():
        for r, row in enumerate(grid):
            if r % 3 == 0:
                yield '+---------+---------+---------+'
            yield ''.join(gen_grid_line(row))
        yield '+---------+---------+---------+'

    for i in clues:
        row, col, d = row_idx_inv(i)
        grid[row][col] = d

    return '\n'.join(gen_grid_lines())


def sudoku_gen(num_puzzles: int) -> Generator[list[int], None, None]:
    start = perf_counter()
    for n in range(1, num_puzzles + 1):
        clues = generate_sudoku()
        time = perf_counter() - start
        print(f'Time {time:0.1f}s: {n} sudokus generated ({n / time: 0.3f} sudokus/s)       ', end='\r')
        yield clues
    print()


def main(generate: int, retain: int):
    start = perf_counter()
    for i, clues in enumerate(nsmallest(retain, sudoku_gen(generate), key=len), start=1):
        print(f'{i})')
        print(f'{len(clues) = }')
        print(make_grid(clues))
    print(f"\nTime = {perf_counter() - start:0.3f} s")


@click.command()
@click.option('--generate', '-g', default=100, help='Number of Sudoku puzzles to generate')
@click.option('--retain', '-r', default=10, help='Number of Sudoku puzzles to retain')
def _main(generate: int, retain: int):
    """
    Generate sudoku puzzles, retain the puzzles that have the fewest clues, and print them.
    """
    main(generate, retain)


if __name__ == '__main__':
    _main()
