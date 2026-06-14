import sys
from enum import Enum
from itertools import chain
from pathlib import Path
from random import shuffle, randrange, sample
from time import perf_counter

import pytest

sys.path.append(str(Path(__file__).parent.parent / 'src'))
from kata_part_3_solution import solve, filter_pieces
from preloaded import Pads, Shapes, check_solution


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

    def apply(self, edge: list[int]):
        return (edge[i] for i in self._indexes)

    def rotate(self, k):
        sign = self._direction
        return Orientations((sign, (self._offset - sign * k * 4) % 16))


def get_edge(color_: str, index_: int, orientation_str_: str) -> list[int]:
    """Returns the edge of the piece with given index of given pad"""
    c = str(index_)
    lines = Pads[color_].value.splitlines()
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
    return list(Orientations[orientation_str_].apply(edge))


def print_edge(edge):
    symbols = ['   ', ' ┌─', '─┐ ', '───', ' └─', ' │ ', '─┼─', '─┘ ']

    e = edge
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
        n = int(''.join(str(m[i - di][j - dj]) for di in (1, 0) for dj in (1, 0)), 2)
        k = n if n <= 7 else 15 ^ n
        return symbols[k]

    for index in range(1, 7):
        print(''.join(c(index, j) for j in range(7))[1:].rstrip())


def print_solution(solution):
    for tile, color, index, orientation_str in solution:
        print(f"Tile {tile}: {color}[{index}]/{orientation_str}")
        print_edge(get_edge(color, index, orientation_str))
        print()


def shape_shuffle(
    shape: list[tuple[int, int, int, int]],
    hints: list[tuple[int, str, int, str]] | None = None,
) -> tuple[list[tuple[int, int, int, int]], list[tuple[int, str, int, str]]]:
    hints = hints or []
    num_tiles = len(shape)
    permutation = list(range(num_tiles))
    shuffle(permutation)
    res = {}
    for tile, neighbors in enumerate(shape):
        res[permutation[tile]] = tuple(permutation[j] for j in neighbors)
    hints_map = {permutation[tile]: (color, index, orientation_str)
                 for tile, color, index, orientation_str in hints}
    for tile, neighbors in res.items():
        k = randrange(4)
        if k > 0:
            res[tile] = tuple(neighbors[(j + k) % 4] for j in range(4))
            if tile in hints_map:
                color, index, orientation_str = hints_map[tile]
                orientation = Orientations[orientation_str].rotate(-k)
                hints_map[tile] = (color, index, orientation.name)
    # noinspection PyTypeChecker
    return [res[i] for i in range(num_tiles)], [(i, *rest) for i, rest in hints_map.items()]


def test_solution_1x1x1_cube():
    _shape = Shapes.CUBE_1x1x1.value
    hints = None
    shape, hints = shape_shuffle(_shape, hints=hints)
    pieces = [(pad.name, i) for pad in Pads if pad.name != 'PURPLE' for i in range(1, 7)]
    start = perf_counter()
    solution = solve(shape, pieces, hints=hints)
    end = perf_counter()
    print(f"Time = {round((end - start) * 1000)} ms")
    assert solution
    errors = check_solution(shape, set(pieces), hints, solution)
    assert not errors, '\n'.join(errors)


def test_solution_1x1x2_prism():
    _shape = Shapes.PRISM_1x1x2.value
    hints = [(7, 'BLUE', 2, 'F0'), (8, 'RED', 5, 'F1'), (9, 'PINK', 4, 'F1')]
    shape, hints = shape_shuffle(_shape, hints=hints)
    pieces = [(pad.name, i) for pad in Pads if pad.name != 'PURPLE' for i in range(1, 7)]
    solution = solve(shape, pieces, hints=hints)
    assert solution
    errors = check_solution(shape, set(pieces), hints, solution)
    assert not errors, '\n'.join(errors)


def test_solution_2x2x2_cube():
    _shape = Shapes.CUBE_2x2x2.value
    _solution = [
        (0, 'GREEN', 2, 'R0'),
        (1, 'PINK', 6, 'R2'),
        (2, 'GREEN', 6, 'R1'),
        (3, 'PINK', 4, 'R3'),
        (4, 'BLUE', 6, 'R0'),
        (5, 'BLUE', 3, 'R2'),
        (6, 'PINK', 2, 'F1'),
        (7, 'GREEN', 1, 'R3'),
        (8, 'YELLOW', 3, 'F1'),
        (9, 'YELLOW', 4, 'R3'),
        (10, 'PINK', 1, 'R1'),
        (11, 'PINK', 3, 'R0'),
        (12, 'YELLOW', 5, 'R0'),
        (13, 'RED', 1, 'R3'),
        (14, 'RED', 6, 'R3'),
        (15, 'YELLOW', 1, 'F3'),
        (16, 'RED', 4, 'R0'),
        (17, 'RED', 2, 'F1'),
        (18, 'YELLOW', 2, 'R1'),
        (19, 'PINK', 5, 'F2'),
        (20, 'BLUE', 2, 'F3'),
        (21, 'BLUE', 5, 'R1'),
        (22, 'BLUE', 4, 'R3'),
        (23, 'GREEN', 5, 'R2'),
    ]
    for _ in range(1):
        hints = sample(_solution, 6)
        shape, hints = shape_shuffle(_shape, hints=hints)
        pieces = [(pad.name, i) for pad in Pads if pad.name != 'PURPLE' for i in range(1, 7)]
        solution = solve(shape, pieces, hints=hints)
        assert solution
        errors = check_solution(shape, set(pieces), hints, solution)
        assert not errors, '\n'.join(errors)


@pytest.mark.skip
def test_solution_2x2x2_cube_w_2_inverted_vertices():
    shape = Shapes.CUBE_2x2x2_WITH_TWO_INVERTED_VERTICES.value
    tack_stitches = [(8 * 16 + 0, 19 * 16 + 4)]
    for _ in range(1):
        pieces = [(pad.name, i) for pad in Pads for i in range(1, 7)
                  if pad.name != 'GREEN']
        subsets = filter_pieces(shape, pieces, hints=[], tack_stitches=tack_stitches)
        necessary = set(pieces)
        print()
        for subset in subsets:
            start = perf_counter()
            solution = solve(shape, list(subset), tack_stitches=tack_stitches)
            end = perf_counter()
            assert solution
            # print_solution(solution)
            if solution:
                print(f"Time = {round((end - start) * 1000)} ms")
                errors = check_solution(shape, set(pieces), [], solution, tack_stitches=tack_stitches)
                assert not errors, '\n'.join(errors)
                necessary = necessary.intersection(subset)
        print(len(necessary), sorted(necessary))


def test_solution_3d_cross():
    _shape = Shapes.THREE_D_CROSS.value
    _solution = [
        (0, 'PINK', 5, 'R0'),
        (1, 'BLUE', 2, 'R1'),
        (2, 'PINK', 1, 'R1'),
        (3, 'GREEN', 1, 'F1'),
        (4, 'PINK', 2, 'F3'),
        (5, 'PURPLE', 6, 'R1'),
        (6, 'PURPLE', 2, 'R0'),
        (7, 'PINK', 3, 'R2'),
        (8, 'BLUE', 4, 'R1'),
        (9, 'GREEN', 4, 'R2'),
        (10, 'GREEN', 2, 'R0'),
        (11, 'PURPLE', 3, 'R2'),
        (12, 'GREEN', 3, 'R0'),
        (13, 'GREEN', 6, 'R1'),
        (14, 'RED', 2, 'F3'),
        (15, 'GREEN', 5, 'F0'),
        (16, 'YELLOW', 3, 'R2'),
        (17, 'RED', 6, 'F2'),
        (18, 'PURPLE', 1, 'R0'),
        (19, 'YELLOW', 5, 'R2'),
        (20, 'YELLOW', 2, 'F0'),
        (21, 'BLUE', 3, 'F1'),
        (22, 'YELLOW', 4, 'F1'),
        (23, 'YELLOW', 1, 'F1'),
        (24, 'PURPLE', 5, 'R3'),
        (25, 'PINK', 4, 'F1'),
        (26, 'BLUE', 5, 'F3'),
        (27, 'PURPLE', 4, 'R0'),
        (28, 'BLUE', 1, 'F2'),
        (29, 'RED', 4, 'F3'),
    ]
    for _ in range(1):
        # hints = sample(_solution, 6)
        hints = []
        shape, hints = shape_shuffle(_shape, hints=hints)
        pieces = [(pad.name, i) for pad in Pads for i in range(1, 7)]
        solution = solve(shape, pieces, hints=hints)
        assert solution
        errors = check_solution(shape, set(pieces), hints, solution)
        assert not errors, '\n'.join(errors)
        print_solution(solution)


def test_solution_prism_3x3x1():
    _shape = Shapes.PRISM_3x3x1.value
    _solution = [
        (0, 'GREEN', 2, 'R0'),
        (1, 'PURPLE', 4, 'R3'),
        (2, 'BLUE', 1, 'F2'),
        (3, 'BLUE', 3, 'R1'),
        (4, 'BLUE', 5, 'F2'),
        (5, 'PINK', 1, 'R1'),
        (6, 'YELLOW', 1, 'F3'),
        (7, 'PURPLE', 5, 'F1'),
        (8, 'PURPLE', 3, 'F1'),
        (9, 'PINK', 2, 'R0'),
        (10, 'GREEN', 6, 'F0'),
        (11, 'PINK', 3, 'R0'),
        (12, 'YELLOW', 5, 'R0'),
        (13, 'RED', 2, 'F0'),
        (14, 'PINK', 5, 'F0'),
        (15, 'PURPLE', 6, 'F2'),
        (16, 'YELLOW', 4, 'R3'),
        (17, 'PINK', 4, 'F1'),
        (18, 'RED', 6, 'R0'),
        (19, 'PURPLE', 1, 'F0'),
        (20, 'PURPLE', 2, 'R3'),
        (21, 'GREEN', 4, 'R2'),
        (22, 'BLUE', 4, 'R2'),
        (23, 'YELLOW', 2, 'R0'),
        (24, 'GREEN', 5, 'R3'),
        (25, 'GREEN', 1, 'R3'),
        (26, 'RED', 4, 'R3'),
        (27, 'GREEN', 3, 'F1'),
        (28, 'BLUE', 2, 'F0'),
        (29, 'YELLOW', 3, 'F3'),
    ]
    for _ in range(1):
        hints = sample(_solution, 7)
        shape, hints = shape_shuffle(_shape, hints=hints)
        # shape = _shape
        pieces = [(pad.name, i) for pad in Pads for i in range(1, 7)]
        solution = solve(shape, pieces, hints=hints)
        assert solution
        errors = check_solution(shape, set(pieces), hints, solution)
        assert not errors, '\n'.join(errors)


@pytest.mark.skip
def test_print_edge():
    pieces = [
        ('BLUE', 1),
        ('GREEN', 2),
        ('GREEN', 3),
        ('GREEN', 4),
        ('GREEN', 5),
        ('PINK', 6),
        ('PURPLE', 1),
        ('PURPLE', 4),
        ('RED', 3),
        ('RED', 5),
        ('YELLOW', 1),
        ('YELLOW', 6),
    ]
    print()
    for color, i in pieces:
        print(f"{color}[{i}]")
        print_edge(get_edge(color, i, 'R0'))
        print()


def test_solution_1x1x1_cube_():
    shape = Shapes.CUBE_1x1x1.value
    # hints = [(2, 'PURPLE', 3, 'F1')]
    hints = []
    pieces = [('PURPLE', i) for i in range(1, 7)]
    start = perf_counter()
    solution = solve(shape, pieces, hints=hints)
    end = perf_counter()
    print(f"\nTime = {round((end - start) * 1000)} ms")
    print_solution(solution)
    assert solution
    errors = check_solution(shape, set(pieces), hints, solution)
    assert not errors, '\n'.join(errors)


@pytest.mark.parametrize('shape', list(Shapes))
# @pytest.mark.parametrize('shape', [Shapes.THREE_STEPS])
def test_solution_no_hints(shape: Shapes):
    print(shape.name)
    shape_, _ = shape_shuffle(shape.value)
    pieces = [(pad.name, i) for pad in Pads for i in range(1, 7)]
    start = perf_counter()
    solution = solve(shape_, pieces)
    exec_time = int((perf_counter() - start) * 1000)
    print(f"Time = {exec_time} ms")
    assert solution
    errors = check_solution(shape_, set(pieces), [], solution)
    assert not errors, '\n'.join(errors)
    # print_solution(solution)


def test_cube_2x2x2():
    pieces = [(pad.name, i) for pad in Pads if pad != Pads.PURPLE for i in range(1, 7)]
    shape = Shapes.CUBE_2x2x2.value
    solution = solve(shape, pieces)
    print()
    print_solution(solution)
