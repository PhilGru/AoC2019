import math
import sys
from typing import Dict, List, NamedTuple, Optional, Set


class Position(NamedTuple):
    x: int
    y: int


def do_step(
    position: Position, direction: str, distance: int, start_distance: int
) -> (Set[Position], Dict[Position, int], Position):
    if direction == "R":
        positions = set()
        distances = {}
        for step in range(distance):
            new_position = Position(x=position.x + (step + 1), y=position.y)
            positions.add(new_position)
            distances[new_position] = start_distance + step + 1
        return positions, distances, new_position
    if direction == "L":
        positions = set()
        distances = {}
        for step in range(distance):
            new_position = Position(x=position.x - (step + 1), y=position.y)
            positions.add(new_position)
            distances[new_position] = start_distance + step + 1
        return positions, distances, new_position
    if direction == "U":
        positions = set()
        distances = {}
        for step in range(distance):
            new_position = Position(x=position.x, y=position.y + (step + 1))
            positions.add(new_position)
            distances[new_position] = start_distance + step + 1
        return positions, distances, new_position
    if direction == "D":
        positions = set()
        distances = {}
        for step in range(distance):
            new_position = Position(x=position.x, y=position.y - (step + 1))
            positions.add(new_position)
            distances[new_position] = start_distance + step + 1
        return positions, distances, new_position


def run_directions(direction: List[str]) -> (Set[Position], Dict[Position, int]):
    last_position = Position(x=0, y=0)
    positions = {last_position}
    distances = {}
    current_distance = 0
    for move in direction:
        new_positions, new_distances, last_position = do_step(
            last_position, move[0], int(move[1:]), current_distance
        )
        current_distance += int(move[1:])
        distances.update(new_distances)
        positions.update(new_positions)
    return positions, distances


def get_min_distance(
    positionss: List[Set[Position]], distancess: List[Dict[Position, int]]
) -> Optional[int]:
    crossings = positionss[0]
    for positions in positionss:
        crossings = crossings.intersection(positions)

    crossings.remove(Position(x=0, y=0))
    distances = {}
    manhatten_distances = {}
    for crossing in crossings:
        manhatten_distances[crossing] = abs(crossing.x) + abs(crossing.y)
        distances[crossing] = sum(
            [distancess_one[crossing] for distancess_one in distancess]
        )
    return min(manhatten_distances.values()), min(distances.values())


def solve(directionss: List[List[str]]) -> Optional[int]:
    positionss, distancess = [], []
    for directions in directionss:
        positions, distances = run_directions(directions)
        positionss.append(positions)
        distancess.append(distances)
    return get_min_distance(positionss, distancess)


if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    puzzle_input = puzzle_input.split()
    directions = [line.split(",") for line in puzzle_input]
    result_1, result_2 = solve(directions)
    print("Result 1:", result_1, "Result 2:", result_2)
