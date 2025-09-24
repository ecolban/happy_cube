from itertools import combinations
from random import choice, shuffle

import pytest

from happy_cube import solve, check_solution
from pads import Pads
from pieces import Orientations
from shapes import Shapes, get_shape_slots, shape_shuffle, get_shape_slots_


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


@pytest.mark.parametrize('shape', [shape_shuffle(shape.value) for shape in Shapes for _ in range(10)])
def test_get_shap_slots(shape):
    shape = shape_shuffle(shape)
    reference = get_shape_slots(shape)
    slots = get_shape_slots_(shape)
    num_slots = 16 * len(shape)
    assert len(slots) == num_slots, "Result does not have the correct length"
    assert all(isinstance(k, int) for k in slots), "Result contains non-ints"
    assert all(0 <= k < num_slots for k in slots), "Result contains numbers out of range"
    for i, j in combinations(range(num_slots), 2):
        equal_in_reference = reference[i] == reference[j]
        if (slots[i] == slots[j]) != equal_in_reference:
            c = '!='[int(equal_in_reference)]
            assert False, f"Expected result[{i}] {c}= result[{j}]"


@pytest.mark.parametrize(
    'pieces', [[(pad.name, index) for index in range(1, 7)] for pad in (Pads.BLUE,)]
)
def test_shuffle(pieces):
    tiles = shape_shuffle(Shapes.CUBE_1x1x1.tiles)
    shuffle(pieces)
    solution = [(t, *pieces[t], choice(list(Orientations)).name) for t in range(6)]
    assert solution
    errors = check_solution(tiles, set(pieces), [], solution)
    assert not errors, f"Errors:\n - {'\n - '.join(errors)}"
