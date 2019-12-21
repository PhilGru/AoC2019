import math
import sys
from typing import Dict, List, NamedTuple, Optional


class Position(NamedTuple):
    x: int
    y: int
    distance: Optional[int]


def manhattan(x: int, y: int) -> int:
    return abs(x) + abs(y)


def make_positions_relative(
    current_asteroid: Position, positions: List[Position]
) -> List[Position]:
    new_positions = [
        Position(
            x=position.x - current_asteroid.x,
            y=position.y - current_asteroid.y,
            distance=None,
        )
        for position in positions
    ]
    right_distances = [
        Position(x=position.x, y=position.y, distance=manhattan(position.x, position.y))
        for position in new_positions
    ]
    return sorted(right_distances, key=lambda x: x.distance)


def is_multiple(x: int, y: int) -> bool:
    if (x == 0) or (y == 0):
        return False
    if x * y < 0:
        return False
    return (x / y).is_integer()


def blocks_line_of_sight(position_1: Position, position_2: Position) -> bool:
    if (position_1.x == 0) and (position_2.x == 0):
        return (position_1.y * position_2.y) > 0
    if (position_1.y == 0) and (position_2.y == 0):
        return (position_1.x * position_2.x) > 0
    if ((position_1.x * position_2.x) > 0) and ((position_1.y * position_2.y) > 0):
        return (position_1.x * position_2.y) == (position_1.y * position_2.x)
    else:
        return False


def parse_input(puzzle_input: List[str]) -> List[Position]:
    positions = []
    for i, row in enumerate(puzzle_input):
        for j, pixel in enumerate(row):
            if pixel == "#":
                positions.append(Position(x=j, y=i, distance=None))
    return positions


def remove_multiples(
    current_asteroid: Position, positions: List[Position], make_relative: bool = True
) -> List[Position]:
    filtered_positions = []
    if make_relative:
        relative_positions = make_positions_relative(current_asteroid, positions)
    else:
        relative_positions = positions
    for position in relative_positions:
        if (position.x == 0) and (position.y == 0):
            continue
        is_blocked = False
        for filtered_position in filtered_positions:
            if blocks_line_of_sight(position, filtered_position):
                is_blocked = True
        if is_blocked == False:
            filtered_positions.append(position)
    return filtered_positions


def count_visible_for_all_asteroids(positions: List[Position]) -> Dict[Position, int]:
    return {
        position: len(remove_multiples(position, positions)) for position in positions
    }


def get_max_visible(counts: Dict[Position, int]) -> int:
    return max(counts.values())


def get_laser_station_and_first_layer(positions: List[Position]) -> Dict[Position, int]:
    first_layers = {
        position: remove_multiples(position, positions) for position in positions
    }
    first_layer_counts = {key: len(val) for key, val in first_layers.items()}
    max_count = max(first_layer_counts.values())
    max_pos = [pos for pos, count in first_layer_counts.items() if (count == max_count)]
    if len(max_pos) == 1:
        return max_pos[0], first_layers[max_pos[0]]
    raise ValueError("Multiple best positions.")


def get_angles(positions: List[Position]) -> Dict[float, Position]:
    return {math.atan2(position.x, position.y): position for position in positions}


#### Checking if the angle goes from the top and then to the right in my coordinates
# positions_test = [Position(0, -1, 0), Position(1, -1, 0), Position(1, 0, 0), Position(1, 1, 0),
#                  Position(0, 1, 0), Position(-1, 1, 0), Position(-1, 0, 0), Position(-1, -1, 0)]
# print(get_angles(positions_test).keys())


def solve_1(puzzle_input: List[str]) -> int:
    parsed_positions = parse_input(puzzle_input)
    counts = count_visible_for_all_asteroids(parsed_positions)
    return get_max_visible(counts)


def solve_2_multiple_rounds(puzzle_input: List[str], nth_asteroid: int) -> int:
    parsed_positions = parse_input(puzzle_input)
    max_pos, _ = get_laser_station_and_first_layer(parsed_positions)
    relative_positions = make_positions_relative(max_pos, parsed_positions)
    asteroids_to_shoot = nth_asteroid
    remaining_asteroids = relative_positions
    i = 0
    while True:
        layer = remove_multiples(max_pos, remaining_asteroids, False)
        if len(layer) >= asteroids_to_shoot:
            angles = get_angles(layer)
            nth_pos = angles[sorted(list(angles.keys()))[::-1][asteroids_to_shoot - 1]]
            pos_og_coordinates = Position(
                nth_pos.x + max_pos.x, nth_pos.y + max_pos.y, None
            )
            return pos_og_coordinates
        else:
            layer = [remaining_asteroids.remove(pos) for pos in layer]
            asteroids_to_shoot = asteroids_to_shoot - len(layer)
        if i > 10000:
            print("Shutting down after 10000 rounds.")
            break


if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    puzzle_input = puzzle_input.split()
    print("Result 1:", solve_1(puzzle_input))
    position = solve_2_multiple_rounds(
        puzzle_input, 200
    )  # Get 200th asteroid that gets shot
    print("Result 2:", position.x * 100 + position.y)
