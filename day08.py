import sys
from collections import Counter
from typing import List

WIDE = 25
TALL = 6


def parse_input_1(puzzle_input: str) -> List[str]:
    nr_elements_in_layer = WIDE * TALL
    nr_layers = len(puzzle_input) // nr_elements_in_layer
    layers = [
        puzzle_input[i * nr_elements_in_layer : (i + 1) * nr_elements_in_layer]
        for i in range(nr_layers)
    ]
    return layers


def min_zeros(layers: List[str]) -> str:
    min_layer = ""
    min_zeros = float("Inf")
    for layer in layers:
        zeros = Counter(layer)["0"]
        if zeros < min_zeros:
            min_zeros = zeros
            min_layer = layer
    return min_layer


def count_digits(layer: str) -> int:
    return Counter(layer)["1"] * Counter(layer)["2"]


def solve_1(puzzle_input: str) -> int:
    layers = parse_input_1(puzzle_input)
    layer = min_zeros(layers)
    return count_digits(layer)


def parse_input_2(puzzle_input: str) -> List[List[str]]:
    nr_elements_in_layer = WIDE * TALL
    nr_layers = len(puzzle_input) // nr_elements_in_layer
    layers = [
        puzzle_input[i * nr_elements_in_layer : (i + 1) * nr_elements_in_layer]
        for i in range(nr_layers)
    ]
    layers = [
        [layer[i * WIDE : (i + 1) * WIDE] for i in range(TALL)] for layer in layers
    ]
    return layers


def get_right_pixel(layers: List[List[str]]) -> List[str]:
    correct_picture = layers[0]
    for layer in layers:
        for i, row in enumerate(layer):
            for j, pixel in enumerate(row):
                if correct_picture[i][j] == "2":
                    correct_picture[i] = (
                        correct_picture[i][:j] + pixel + correct_picture[i][(j + 1) :]
                    )
    return correct_picture


def show_picture(layer: List[str]) -> None:
    for row in layer:
        new_row = row.replace("2", "2__")
        new_row = new_row.replace("1", "8__")
        new_row = new_row.replace("0", "___")
        print(new_row)
    print()


def solve_2(puzzle_input: str) -> List[str]:
    layers = parse_input_2(puzzle_input)
    picture = get_right_pixel(layers)
    show_picture(picture)


if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    print("Result 1:", solve_1(puzzle_input))
    print("Result 2:")
    solve_2(puzzle_input)
