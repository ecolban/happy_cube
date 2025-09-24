from random import randrange, choice

import pytest

from kata_part_2_solution import get_covered_shape_slots, get_edge, Piece
from preloaded import Pads
from shapes import Shapes, get_shape_slots, shape_shuffle

COLORS = ['BLUE', 'GREEN', 'PINK', 'PURPLE', 'RED', 'YELLOW']
ORIENTATIONS = ['R0', 'R1', 'R2', 'R3', 'F0', 'F1', 'F2', 'F3']


@pytest.mark.parametrize(
    'shape', list(Shapes)
)
def test_get_covered_shape_slots(shape):
    slot_map = get_shape_slots(shape_shuffle(shape.value))
    tile = randrange(len(shape.value))
    orientation = choice(ORIENTATIONS)
    color = choice(COLORS)
    index = randrange(1, 7)
    covered_slots = get_covered_shape_slots(tile, color, index, orientation, slot_map)
    edge = Piece(color, index, orientation).edge
    assert sum(edge) == len(covered_slots)
    for i, v in enumerate(edge):
        assert int(slot_map[16 * tile + i] in covered_slots) == v


@pytest.mark.parametrize('pad', list(Pads))
@pytest.mark.parametrize('index', list(range(1, 7)))
def test_get_edge(pad, index):
    edge = list(get_edge(pad, index))
    assert len(edge) == 16
    assert set(edge) == {0, 1}
    for i in range(0, 16, 4):
        assert 0 in edge[i: i + 4]
        assert 1 in edge[i: i + 4]
