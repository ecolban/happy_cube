import sys
from pathlib import Path
from random import sample, shuffle, randrange

import pytest

SRC = str(Path(__file__).parent.parent / 'src')
sys.path.append(SRC)

from happy_cube_solver import solve, solve_one, HintSpec, print_edge, get_edge, Orientations
from happy_cube_solution_checker import check_solution
from shapes import Shapes
from pads import PadsDublin as Pads, PadsSkatoy


def print_solution(solution):
    for tile, pad, index, orientation_str in solution:
        print(f"Tile {tile}: {pad}[{index}]/{orientation_str}")
        print_edge(get_edge(pad, index, orientation_str))
        print()


def shape_shuffle(
    shape: list[tuple[int, int, int, int]],
    hints: list[tuple[int, str, int, str]] | None = None,
) -> tuple[list[tuple[int, int, int, int]], list[HintSpec]]:
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


@pytest.mark.parametrize('pieces', [
    *([(pad, i) for i in range(1, 7)] for pad in Pads),
])
def test_solution_1x1x1_cube(pieces):
    _shape = Shapes.CUBE_1x1x1.value
    hints = None
    shape, hints = shape_shuffle(_shape, hints=hints)
    solution = next(solve(shape, pieces, hints=hints))
    assert solution
    errors = check_solution(shape, set(pieces), hints, solution)
    assert not errors, '\n'.join(errors)


def test_solution_two_1x1x1_cubes():
    _shape = Shapes.TWO_CUBE_1x1x1.value
    hints = None
    shape, hints = shape_shuffle(_shape, hints=hints)
    pieces = [(pad, i) for pad in (Pads.BLUE, Pads.YELLOW) for i in range(1, 7)]
    solution = next(solve(shape, pieces, hints=hints))
    assert solution
    errors = check_solution(shape, set(pieces), hints, solution)
    assert not errors, '\n'.join(errors)


@pytest.mark.skip
def test_solution_three_1x1x1_cubes():
    _shape = Shapes.THREE_CUBE_1x1x1.value
    hints = None
    # shape, hints = shape_shuffle(_shape, hints=hints)
    shape = _shape
    pieces = [(pad, i) for pad in Pads for i in range(1, 7)]
    solution = next(solve(shape, pieces, hints=hints))
    assert solution
    errors = check_solution(shape, set(pieces), hints, solution)
    assert not errors, '\n'.join(errors)


@pytest.mark.skipif(Pads is PadsSkatoy, reason='Cannot be solved with PadsSkatoy')
def test_solution_1x1x2_prism():
    _shape = Shapes.PRISM_1x1x2.value
    shape, hints = shape_shuffle(_shape, hints=[])
    pieces = [(pad, i) for pad in Pads if pad.name != 'PURPLE' for i in range(1, 7)]
    solution = next(solve(shape, pieces, hints=hints))
    assert solution
    errors = check_solution(shape, set(pieces), hints, solution)
    assert not errors, '\n'.join(errors)


def test_solution_1x1x4_prism():
    _shape = Shapes.PRISM_1x1x4.value
    shape, hints = shape_shuffle(_shape, hints=[])
    pieces = [(pad, i) for pad in Pads if pad.name != 'PURPLE' for i in range(1, 7)]
    solution = next(solve(shape, pieces, hints=hints))
    assert solution
    errors = check_solution(shape, set(pieces), hints, solution)
    assert not errors, '\n'.join(errors)


def test_solution_1x1x5_prism():
    _shape = Shapes.PRISM_1x1x5.value
    # hints = [(7, Pads.BLUE, 2, 'F0'), (8, Pads.RED, 5, 'F1'), (9, Pads.PINK, 4, 'F1')]
    # shape, hints = shape_shuffle(_shape, hints=hints)
    shape, hints = _shape, []
    pieces = [(pad, i) for pad in Pads for i in range(1, 7)]
    solution = next(solve(shape, pieces, hints=hints))
    assert solution
    errors = check_solution(shape, set(pieces), hints, solution)
    assert not errors, '\n'.join(errors)


def test_solution_t_shape():
    _shape = Shapes.T_SHAPE.value
    # hints = [(7, Pads.BLUE, 2, 'F0'), (8, Pads.RED, 5, 'F1'), (9, Pads.PINK, 4, 'F1')]
    # shape, hints = shape_shuffle(_shape, hints=hints)
    shape, hints = _shape, []
    pieces = [(pad, i) for pad in Pads for i in range(1, 7)]
    solution = next(solve(shape, pieces, hints=hints))
    assert solution
    errors = check_solution(shape, set(pieces), hints, solution)
    assert not errors, '\n'.join(errors)


@pytest.mark.skipif(Pads is PadsSkatoy, reason='Cannot be solved with PadsSkatoy')
def test_solution_2x2x2_cube():
    shape = Shapes.CUBE_2x2x2.value
    _solution = [
        (0, Pads.GREEN, 2, 'R0'),
        (1, Pads.PINK, 6, 'R2'),
        (2, Pads.GREEN, 6, 'R1'),
        (3, Pads.PINK, 4, 'R3'),
        (4, Pads.BLUE, 6, 'R0'),
        (5, Pads.BLUE, 3, 'R2'),
        (6, Pads.PINK, 2, 'F1'),
        (7, Pads.GREEN, 1, 'R3'),
        (8, Pads.YELLOW, 3, 'F1'),
        (9, Pads.YELLOW, 4, 'R3'),
        (10, Pads.PINK, 1, 'R1'),
        (11, Pads.PINK, 3, 'R0'),
        (12, Pads.YELLOW, 5, 'R0'),
        (13, Pads.RED, 1, 'R3'),
        (14, Pads.RED, 6, 'R3'),
        (15, Pads.YELLOW, 1, 'F3'),
        (16, Pads.RED, 4, 'R0'),
        (17, Pads.RED, 2, 'F1'),
        (18, Pads.YELLOW, 2, 'R1'),
        (19, Pads.PINK, 5, 'F2'),
        (20, Pads.BLUE, 2, 'F3'),
        (21, Pads.BLUE, 5, 'R1'),
        (22, Pads.BLUE, 4, 'R3'),
        (23, Pads.GREEN, 5, 'R2'),
    ]
    for _ in range(1):
        hints = sample(_solution, 12)
        shape, hints = shape_shuffle(shape, hints=hints)
        pieces = [(pad, i) for pad in Pads for i in range(1, 7)]
        solution = solve_one(shape, pieces, hints=hints)
        assert solution
        errors = check_solution(shape, set(pieces), hints, solution)
        assert not errors, '\n'.join(errors)


@pytest.mark.skipif(Pads is PadsSkatoy, reason='Cannot be solved with PadsSkatoy')
def test_solution_3d_cross():
    shape = Shapes.THREE_D_CROSS.value
    _solution = [
        (0, Pads.PINK, 5, 'R0'),
        (1, Pads.BLUE, 2, 'R1'),
        (2, Pads.PINK, 1, 'R1'),
        (3, Pads.GREEN, 1, 'F1'),
        (4, Pads.PINK, 2, 'F3'),
        (5, Pads.PURPLE, 6, 'R1'),
        (6, Pads.PURPLE, 2, 'R0'),
        (7, Pads.PINK, 3, 'R2'),
        (8, Pads.BLUE, 4, 'R1'),
        (9, Pads.GREEN, 4, 'R2'),
        (10, Pads.GREEN, 2, 'R0'),
        (11, Pads.PURPLE, 3, 'R2'),
        (12, Pads.GREEN, 3, 'R0'),
        (13, Pads.GREEN, 6, 'R1'),
        (14, Pads.RED, 2, 'F3'),
        (15, Pads.GREEN, 5, 'F0'),
        (16, Pads.YELLOW, 3, 'R2'),
        (17, Pads.RED, 6, 'F2'),
        (18, Pads.PURPLE, 1, 'R0'),
        (19, Pads.YELLOW, 5, 'R2'),
        (20, Pads.YELLOW, 2, 'F0'),
        (21, Pads.BLUE, 3, 'F1'),
        (22, Pads.YELLOW, 4, 'F1'),
        (23, Pads.YELLOW, 1, 'F1'),
        (24, Pads.PURPLE, 5, 'R3'),
        (25, Pads.PINK, 4, 'F1'),
        (26, Pads.BLUE, 5, 'F3'),
        (27, Pads.PURPLE, 4, 'R0'),
        (28, Pads.BLUE, 1, 'F2'),
        (29, Pads.RED, 4, 'F3'),
    ]
    for _ in range(1):
        hints = sample(_solution, 6)
        shape, hints = shape_shuffle(shape, hints=hints)
        pieces = [(pad, i) for pad in Pads for i in range(1, 7)]
        solution = solve_one(shape, pieces, hints=hints)
        assert solution
        errors = check_solution(shape, set(pieces), hints, solution)
        assert not errors, '\n'.join(errors)


@pytest.mark.skipif(Pads is PadsSkatoy, reason='Cannot be solved with PadsSkatoy')
def test_solution_prism_3x3x1():
    shape = Shapes.PRISM_3x3x1.value
    _solution = [
        (0, Pads.GREEN, 2, 'R0'),
        (1, Pads.PURPLE, 4, 'R3'),
        (2, Pads.BLUE, 1, 'F2'),
        (3, Pads.BLUE, 3, 'R1'),
        (4, Pads.BLUE, 5, 'F2'),
        (5, Pads.PINK, 1, 'R1'),
        (6, Pads.YELLOW, 1, 'F3'),
        (7, Pads.PURPLE, 5, 'F1'),
        (8, Pads.PURPLE, 3, 'F1'),
        (9, Pads.PINK, 2, 'R0'),
        (10, Pads.GREEN, 6, 'F0'),
        (11, Pads.PINK, 3, 'R0'),
        (12, Pads.YELLOW, 5, 'R0'),
        (13, Pads.RED, 2, 'F0'),
        (14, Pads.PINK, 5, 'F0'),
        (15, Pads.PURPLE, 6, 'F2'),
        (16, Pads.YELLOW, 4, 'R3'),
        (17, Pads.PINK, 4, 'F1'),
        (18, Pads.RED, 6, 'R0'),
        (19, Pads.PURPLE, 1, 'F0'),
        (20, Pads.PURPLE, 2, 'R3'),
        (21, Pads.GREEN, 4, 'R2'),
        (22, Pads.BLUE, 4, 'R2'),
        (23, Pads.YELLOW, 2, 'R0'),
        (24, Pads.GREEN, 5, 'R3'),
        (25, Pads.GREEN, 1, 'R3'),
        (26, Pads.RED, 4, 'R3'),
        (27, Pads.GREEN, 3, 'F1'),
        (28, Pads.BLUE, 2, 'F0'),
        (29, Pads.YELLOW, 3, 'F3'),
    ]
    for _ in range(1):
        hints = sample(_solution, 7)
        shape, hints = shape_shuffle(shape, hints=hints)
        # hints = []
        pieces = [(pad, i) for pad in Pads for i in range(1, 7)]
        solution = solve_one(shape, pieces, hints=hints)
        assert solution
        errors = check_solution(shape, set(pieces), hints, solution)
        assert not errors, '\n'.join(errors)


@pytest.mark.skip
def test_print_edge():
    pieces = [
        (Pads.BLUE, 1),
        (Pads.BLUE, 2),
        (Pads.BLUE, 3),
        (Pads.BLUE, 4),
        (Pads.BLUE, 5),
        (Pads.BLUE, 6),
        (Pads.PURPLE, 1),
        (Pads.PURPLE, 4),
        (Pads.RED, 3),
        (Pads.RED, 5),
        (Pads.YELLOW, 1),
        (Pads.YELLOW, 6),
    ]
    print()
    for pad, i in pieces:
        print(f"{pad.name}[{i}]")
        print_edge(get_edge(pad, i, 'R0'))
        print()


@pytest.mark.parametrize('shape', [
    Shapes.CUBE_1x1x1,
    Shapes.CUBE_1x1x1_WITH_FIVE_CUBE_1x1x1_OUTGROWTHS,
    Shapes.CUBE_2x2x2,
    Shapes.CUBE_2x2x2_WITH_CUBE_1x1x1_OUTGROWTH, # Not with PadsSkatoy
    Shapes.CUBE_2x2x2_WITH_ONE_INVERTED_VERTEX,
    Shapes.CUBE_2x2x2_WITH_TWO_INVERTED_VERTICES,
    Shapes.C_SHAPE,
    Shapes.LIGHTNING_BOLT,
    Shapes.L_SHAPE,
    Shapes.PRISM_1x1x2,
    Shapes.PRISM_1x1x3, # Not with PadsSkatoy
    Shapes.PRISM_1x1x4,
    Shapes.PRISM_1x1x5,
    Shapes.PRISM_3x3x1, # Not with PadsSkatoy
    Shapes.THREE_D_CORNER,
    Shapes.THREE_D_CROSS, # Not with PadsSkatoy
    Shapes.THREE_STEPS,
    Shapes.T_SHAPE,
    Shapes.W_SHAPE,
    Shapes.X_SHAPE,
])
def test_solution_no_hints(shape: Shapes):
    print(shape.name)
    shape_, _ = shape_shuffle(shape.value)
    pieces = [(pad, i) for pad in Pads for i in range(1, 7)]
    solution = solve_one(shape_, pieces)
    assert solution
    errors = check_solution(shape_, set(pieces), [], solution)
    assert not errors, '\n'.join(errors)


@pytest.mark.skip
def test_cube_2x2x2_w_2_inverted_vertices():
    pieces = [(pad, i) for pad in Pads for i in range(1, 7)]
    shape = Shapes.CUBE_2x2x2_WITH_TWO_INVERTED_VERTICES.value
    tack_stitches = [(8 * 16 + 0, 19 * 16 + 4)]
    solutions = solve(shape, pieces, tack_stitches=tack_stitches)
    solution_set = {
        tuple(next(solutions)) for _ in range(100)
    }
    assert len(solution_set) == 100
    for solution in solution_set:
        errors = check_solution(shape, pieces, [], solution=solution, tack_stitches=tack_stitches)
        assert not errors


def test_cube_2x2x2_w_1_inverted_vertex():
    pieces = [(pad, i) for pad in Pads for i in range(1, 7)]
    shape = Shapes.CUBE_2x2x2_WITH_ONE_INVERTED_VERTEX.value
    solution = next(solve(shape, pieces))
    assert solution
    errors = check_solution(shape, pieces, hints=[], solution=solution)
    assert not errors
    print()
