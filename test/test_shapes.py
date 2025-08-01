import pytest

from happy_cube import solve, check_solution
from pads import Pads
from pieces import Piece
from puzzles import Shapes, get_cubits, shape_shuffle


@pytest.mark.parametrize(
    ('shape', 'expected_corner_cubits'),
    [
        (Shapes.SHAPE1, 8),
        (Shapes.SHAPE2, 12),
        (Shapes.SHAPE3, 16),
        (Shapes.SHAPE4, 26),
        (Shapes.SHAPE4b, 30),
        (Shapes.SHAPE5, 28),
        (Shapes.SHAPE6, 32),
        (Shapes.SHAPE7, 28),
    ]
)
def test_edge_cubits(shape, expected_corner_cubits):
    cubits = get_cubits(shape.tiles)
    assert len(set(cubits)) == len(shape.tiles) * 6 + expected_corner_cubits
    c = set(cubits[16 * i + j] for i, _ in enumerate(shape.tiles) for j in range(0, 16, 4))
    assert len(c) == expected_corner_cubits


def test_shuffle():
    tiles = shape_shuffle(Shapes.SHAPE1.tiles)
    pieces = [Piece(Pads['RED'], i) for i in range(6)]
    solution = next(solve(tiles, pieces))
    assert solution
    assert check_solution(tiles=tiles, pieces={(piece.color, piece.index) for piece in pieces}, solution=solution)
