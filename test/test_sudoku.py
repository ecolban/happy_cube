import sys
from collections import Counter
from pathlib import Path

import pytest

SRC_PATH = Path(__file__).parent.parent / 'src'
sys.path.append(str(SRC_PATH))
from sudoku import solve_sudoku, row_idx, sudoku_as_str


def check_solution(solution_str: str):
    errors = []

    def row(i: int):
        return solution_str[i * 9: (i + 1) * 9]

    def column(j: int):
        return [solution_str[i * 9 + j] for i in range(9)]

    def box(k: int):
        q, r = divmod(k, 3)
        row_start = 3 * q
        col_start = 3 * r
        return [solution_str[(row_start + i) * 9 + col_start + j] for i in range(3) for j in range(3)]

    if len(solution_str) != 81:
        return "Solution must assign numbers to 81 cells"

    for i in range(9):
        for j in range(9):
            n = solution_str[9 * i + j]
            if n not in '123456789':
                errors.append(f"Value {n} assigned to R{i + 1}C{j + 1} is not a number between 1 and 9")

    for f in (row, column, box):
        for i in range(9):
            ns = Counter(f(i))
            for n in '123456789':
                if n not in ns:
                    errors.append(f"Number {n} is missing in {f.__name__} {i + 1}")
                elif ns[n] != 1:
                    errors.append(f"Number {n} appears {ns[n]} times in {f.__name__} {i + 1}.")

    assert not errors, '\n'.join(errors)


@pytest.mark.parametrize('clues_str', [
    '673800900000400000100006000002000040048070300000001020800000000000020007000609200',
    '700304806000000030900500000000040010006073000008000050050090081020000000000000509',
    '500097040000000007000000010020000000098053000100080006204300000003000900000010084',
    '076080900000000000000009001020000008000900050504000027200700640000003000801020000',
    '004751008002000000000000000673000000040030100000000090080003000900006080005012300',
    '060490003900000500500030002091600000200010008000000000080006241000700050003000000',
    '706240090800000004000000002938001000000000000000000705000010509090400300002607000',
    '085107006900000000002000000703405010001000000500030800090070300000806000000500007',
    '047018002000000000000600030000095000008300000026007100165000004030001000000009700',
    '180900705000020000000000000007010900090000240000004050070805060032000000508300000',
    '980060007070300000003080609000600028050000000600070400000043102400002360001700000',
    '020090001001200000097000050000706003200310000006004800005030007900070040700800206',
    '605041700000000080400005000007000203050007008000090000000800000200000501900006040',
])
def test_solve_sudoku(clues_str):
    clues = [row_idx(r, c, d) for r in range(9) for c in range(9) if (d := int(clues_str[9 * r + c])) > 0]
    solutions = list(solve_sudoku(clues))
    assert len(solutions) == 1
    solution = solutions[0]
    solution_str = sudoku_as_str(solution)

    # the solution is consistent with the clues
    for c1, c2 in zip(clues_str, solution_str):
        assert c1 in ('0', c2), "Solution is not compatible with given clues"
    check_solution(solution_str)


def test_get_errors():
    solution_str = '673812954285097136194536871712368549948275361356941728821754693569123487437689215'
    with pytest.raises(AssertionError) as e:
        check_solution(solution_str)
