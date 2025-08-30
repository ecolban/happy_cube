from itertools import combinations

import pytest

from happy_cube import solve
from pads import Pads
from pieces import Piece
from shapes import Shapes, get_shape_slots, shape_shuffle, check_solution


@pytest.mark.parametrize(
    ('shape', 'expected_corner_slots'),
    [
        (Shapes.CUBE_1x1x1.value, 8),
        (Shapes.PRISM_1x1x2.value, 12),
        (Shapes.PRISM_1x1x3.value, 16),
        (Shapes.CUBE_2x2x2.value, 26),
        (Shapes.CUBE_2x2x2_WITH_CUBE_1x1x1_OUTGROWTH.value, 30),
        (Shapes.CUBE_1x1x1_WITH_FIVE_CUBE_1x1x1_OUTGROWTHS.value, 28),
        (Shapes.THREE_D_CROSS.value, 32),
        (Shapes.CUBE_1x1x1_WITH_THREE_CUBE_1x1x1_OUTGROWTHS.value, 28),
    ]
)
def test_shape_corners(shape, expected_corner_slots):
    slots = get_shape_slots(shape)
    assert len(set(slots)) == len(shape) * 6 + expected_corner_slots
    c = set(slots[16 * i + j] for i, _ in enumerate(shape) for j in range(0, 16, 4))
    assert len(c) == expected_corner_slots


@pytest.mark.parametrize(
    ('shape', 'a_solution'),
    [
        (Shapes.CUBE_1x1x1.value,
         [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0, 15, 14, 13, 12, 16, 17, 18, 19, 20, 21, 22, 23, 24,
          25, 26, 12, 11, 10, 9, 8, 27, 28, 29, 30, 31, 32, 33, 19, 18, 17, 16, 8, 7, 6, 5, 4, 34, 35, 36, 37, 38, 39,
          40, 30, 29, 28, 27, 19, 33, 32, 31, 30, 40, 39, 38, 37, 41, 42, 43, 23, 22, 21, 20, 23, 43, 42, 41, 37, 36,
          35, 34, 4, 3, 2, 1, 0, 26, 25, 24]),
    ]
)
def test_get_shap_slots(shape, a_solution):
    slots = get_shape_slots(shape)
    num_slots = 16 * len(shape)
    assert len(slots) == num_slots, "Result does not have the correct length"
    assert all(isinstance(k, int) for k in slots), "Result contains non-ints"
    assert all(0 <= k < num_slots for k in slots), "Result contains numbers out of range"
    for i, j in combinations(range(num_slots), 2):
        must_be_equal = a_solution[i] == a_solution[j]
        if (slots[i] == slots[j]) != must_be_equal:
            c = '!='[must_be_equal]
            assert False, f"Expected result[{i}] {c}= result[{j}]"


@pytest.mark.parametrize(
    'pieces', [[(pad.name, index) for index in range(6)] for pad in Pads]
)
def test_shuffle(pieces):
    shape = shape_shuffle(Shapes.CUBE_1x1x1.value)
    solution = next(solve(shape, pieces), None)
    assert solution
    assert check_solution(shape, set(pieces), solution)
