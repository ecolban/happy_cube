import pytest

from pads import Pads, Pads2


@pytest.mark.parametrize(
    "pads_obj", Pads
)
def test_pad(pads_obj):
    pad = pads_obj.parse()
    assert sum(1 for _ in pad) == 6
    for i, pad_piece in enumerate(pad):
        assert pad[i] == pad_piece
        assert isinstance(pad_piece, str)
        lines = pad_piece.splitlines()
        assert len(lines) == 5
        assert all(len(line) == 5 for line in lines)
        assert all(c in '01' for line in lines for c in line)


@pytest.mark.parametrize(
    "pads_obj", Pads2
)
def test_pads2(pads_obj):
    pad = pads_obj.parse()
    assert sum(1 for _ in pad) == 6
    for i, pad_piece in enumerate(pad):
        assert pad[i] == pad_piece
        assert isinstance(pad_piece, str)
        lines = pad_piece.splitlines()
        assert len(lines) == 5
        assert all(len(line) == 5 for line in lines)
        assert all(c in '01' for line in lines for c in line)
