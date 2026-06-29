import sys
from pathlib import Path

import pytest

SRC = Path(__file__).parent.parent / 'src'

sys.path.append(str(SRC))

from pads import PadsDublin as Pads, PadsBase


@pytest.mark.parametrize('pad', Pads)
def test_pad(pad: Pads):
    assert len(pad) == 7
    for i in range(1, 7):
        piece_edge = pad[i]
        assert isinstance(piece_edge, list)
        assert len(piece_edge) == 16
        assert set(piece_edge) == {0, 1}


@pytest.mark.parametrize('pad', Pads)
def test_pad_str(pad: PadsBase):
    print(f'\n{pad.name}')
    s = str(pad)
    lines = s.splitlines()
    assert len(lines) == 12
    for line in lines:
        assert len(line) == 3 * 16

