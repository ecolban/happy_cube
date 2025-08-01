import pytest

from pieces import Orientations
from pads import Pads
from pieces import Piece


@pytest.mark.parametrize(
    'pad', list(Pads)
)
@pytest.mark.parametrize(
    ('orientation', 'expected_mapping'), [
        (Orientations.ID, lambda i: i),
        (Orientations.R1, lambda i: (i + 4) % 16),
        (Orientations.R2, lambda i: (i + 8) % 16),
        (Orientations.R3, lambda i: (i + 12) % 16),
        (Orientations.F1, lambda i: (-i + 4) % 16),
        (Orientations.F2, lambda i: (-i + 8) % 16),
        (Orientations.F3, lambda i: (-i + 12) % 16),
        (Orientations.F4, lambda i: -i % 16),
    ]
)
def test_piece(pad: Pads, orientation, expected_mapping):
    color = pad.name
    for index, pattern in enumerate(pad.value):
        piece = Piece(pattern, color, index)
        assert isinstance(piece.edge, tuple)
        assert all(j in (0, 1) for j in piece.edge)
        edge_before = piece.edge
        piece.orientation = orientation
        edge_after = piece.edge
        assert all(edge_after[expected_mapping(i)] == edge_before[i] for i in range(16))