import sys
from pathlib import Path

import pytest

SRC = Path(__file__).parent.parent / 'src'

sys.path.append(str(SRC))

from pads import Pads

COLORS = ['BLUE', 'GREEN', 'PINK', 'PURPLE', 'RED', 'YELLOW']


@pytest.mark.parametrize('color', COLORS)
def test_pad(color):
    pad = Pads[color]
    assert len(pad) == 7
    for i in range(1, 7):
        piece_edge = pad[i]
        assert isinstance(piece_edge, list)
        assert len(piece_edge) == 16
        assert set(piece_edge) == {0, 1}


@pytest.mark.parametrize('color', COLORS)
def test_pad_str(color):
    pad = Pads[color]
    print(pad)
    s = str(pad)
    lines = s.splitlines()
    assert len(lines) == 12
    for line in lines:
        assert len(line) == 3 * 16


def test_piece():
    assert Pads.YELLOW[1] == [0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0]
    assert Pads.YELLOW[2] == [0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0]
    assert Pads.YELLOW[3] == [1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1]
    assert Pads.YELLOW[4] == [0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1]
    assert Pads.YELLOW[5] == [0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1]
    assert Pads.YELLOW[6] == [0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0]
