import itertools
import sys
from typing import Iterable

import matplotlib.pyplot as plt

BASE_PATTERN = [0, 1, 0, -1]


def get_nth_base_pattern(n: int) -> str:
    return list(
        itertools.chain.from_iterable(([[digit] * n for digit in BASE_PATTERN]))
    )


def get_nth_pattern(n: int) -> Iterable:
    return itertools.cycle(get_nth_base_pattern(n))


def apply_pattern(digits: str) -> str:
    new_digits = ""
    for l in range(len(digits)):
        pattern = get_nth_pattern(l + 1)
        next(pattern)
        new_digit = 0
        for i, (digit, pattern_digit) in enumerate(zip(digits, pattern)):
            if (pattern_digit == 0) or (digit == 0):
                continue
            new_digit += int(digit) * int(pattern_digit)
        new_digits = new_digits + str(new_digit)[-1]
    return new_digits


def solve_1(puzzle_input: str) -> str:
    digits = puzzle_input
    for i in range(100):
        digits = apply_pattern(digits)
    return digits


def get_n_to_last_for_k_phases(digits: str, n: int, k: int):
    digits = digits[-n:]
    new_digits = digits.copy()
    for phase in range(k):
        last_digit = new_digits[-1]
        digits = new_digits.copy()
        for back in range(2, n + 1):
            new_digits[-back] = abs(last_digit + new_digits[-back]) % 10
            last_digit = new_digits[-back]
    return new_digits


def solve_2(puzzle_input: str) -> str:
    offset = int(puzzle_input[:7])
    nr_digits_from_end = 10000 * len(puzzle_input) - offset
    repeats = nr_digits_from_end // 32 + 1
    digits = [int(digit) for digit in puzzle_input]
    digits = list(itertools.chain.from_iterable(itertools.repeat(digits, repeats)))
    res = get_n_to_last_for_k_phases(digits, nr_digits_from_end, 100)[0:10]
    return res


# Tests for part 1
# print(solve_1("80871224585914546619083218645595"))
# print(solve_1("19617804207202209144916044189917"))
# print(solve_1("69317163492948606335995924319873"))

# Tests for part 2
# print(solve_2("03036732577212944063491565474664"))
# print(solve_2("02935109699940807407585447034323"))
# print(solve_2("03081770884921959731165446850517"))

if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    print("Result 1:", solve_1(puzzle_input)[:8])
    print("Result 2:", solve_2(puzzle_input))
