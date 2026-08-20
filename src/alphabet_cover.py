from pathlib import Path
from string import ascii_lowercase
from time import perf_counter

# from py_dlx_solver import DlxSolver
from rust_dlx_lib import DlxSolver

DATA_PATH = Path(__file__).parent.parent / "data"
with open(DATA_PATH / 'wordle-words.txt', mode='r') as f:
    WORDLE_WORDS = sorted(w for line in f if len(set((w := line.strip()))) == 5)
with open(DATA_PATH / "allowed_words.txt") as f:
    ALLOWED_WORDS = sorted(w for line in f if len(set((w := line.strip()))) == 5)
ALPHABET_POSITION = {letter: i for i, letter in enumerate(ascii_lowercase)}


def create_matrix(words):
    matrix = []
    words_kept = []
    anagrams = {}
    for word in words:
        if ''.join(sorted(word)) in anagrams:
            continue
        anagrams[''.join(sorted(word))] = word
        words_kept.append(word)
        row = [0] * 27
        for letter in word:
            row[ALPHABET_POSITION[letter]] = 1
        matrix.append(row)
    # Joker rows
    joker_column = 26
    for letter in ascii_lowercase:
        row = [0] * 27
        row[ALPHABET_POSITION[letter]] = 1
        row[joker_column] = 1
        matrix.append(row)

    return matrix, words_kept


def solve():
    matrix, words = create_matrix(ALLOWED_WORDS)
    solver = DlxSolver(matrix)
    num_words = len(words)
    for solution in solver:
        yield [words[i] if i < num_words else ascii_lowercase[i - num_words] for i in solution]


if __name__ == '__main__':
    start = perf_counter()
    solution_words = set()
    for solution in solve():
        print(solution)
        for word in solution:
            if len(word) == 5:
                solution_words.add(word)
    print(f'Time = {round((perf_counter() - start) * 1000):d} ms')
    print(f'{sorted(solution_words) = }')
