from string import ascii_lowercase
from time import perf_counter

# from py_dlx_solver import DlxSolver
from rust_dlx_lib import DlxSolver

from words import ALLOWED_WORDS

LETTER_IN_ALPHABET_POSITION = {letter: i for i, letter in enumerate(ascii_lowercase)}


def create_matrix(words):
    matrix = []
    row_map = []
    anagrams = set()
    for word in words:
        key = tuple(sorted(word))
        if key in anagrams:
            continue
        anagrams.add(key)
        row = [0] * 27
        for letter in word:
            row[LETTER_IN_ALPHABET_POSITION[letter]] = 1
        matrix.append(row)
        row_map.append(word)
    # Joker rows
    joker_column = 26
    for letter in ascii_lowercase:
        row = [0] * 27
        row[LETTER_IN_ALPHABET_POSITION[letter]] = 1
        row[joker_column] = 1
        matrix.append(row)
        row_map.append(letter)

    return matrix, row_map


def solve():
    matrix, row_map = create_matrix(ALLOWED_WORDS)
    solver = DlxSolver(matrix)
    for solution in solver:
        yield [row_map[i] for i in solution]


if __name__ == '__main__':
    start = perf_counter()
    for i, solution in enumerate(solve(), start=1):
        print(i, solution)
    print(f'Time = {round((perf_counter() - start) * 1000):d} ms')
