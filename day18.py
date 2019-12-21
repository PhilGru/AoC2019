import copy
import pickle
import string
import sys
from typing import Dict, List, NamedTuple, Optional, Set, Tuple


class Position(NamedTuple):
    x: int
    y: int


class Labyrinth(NamedTuple):
    walls: Set
    ground: Set
    doors: Dict[str, Position]
    keys: Dict[str, Position]


def find_shortest_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if start not in graph.keys():
        return None
    shortest = None
    for node in graph[start]:
        if node not in path:
            newpath = find_shortest_path(graph, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest


def add_neighbours(
    i: int,
    j: int,
    x_shift: int,
    y_shift: int,
    lines: List[str],
    graph: Dict[Position, List[Position]],
):
    current_neighbour = lines[j + y_shift][i + x_shift]
    current_position = Position(x=i + x_shift, y=j + y_shift)
    if current_neighbour in [".", "@"]:
        graph[Position(x=i, y=j)].append(current_position)
    if current_neighbour in string.ascii_lowercase:
        graph[Position(x=i, y=j)].append(current_position)
    # Including Doors
    if current_neighbour in string.ascii_uppercase:
        graph[Position(x=i, y=j)].append(current_position)
    return graph


def build_graph(lines: List[str]):
    graph = {}
    labyrinth = Labyrinth(walls=set(), ground=set(), doors={}, keys={})
    for j, line in enumerate(lines):
        for i, pixel in enumerate(line):
            current_position = Position(x=i, y=j)
            graph[current_position] = []
            if pixel == ".":
                labyrinth.ground.add(current_position)
            if pixel in string.ascii_uppercase:
                labyrinth.doors[pixel] = current_position
            if pixel in string.ascii_lowercase:
                labyrinth.keys[pixel] = current_position
            if pixel == "@":
                start_position = current_position
            if pixel == "#":
                labyrinth.walls.add(current_position)
                continue

            if i == 0:
                x_shifts = [1]
            elif i == (len(line) - 1):
                x_shifts = [-1]
            else:
                x_shifts = [-1, 1]

            if j == 0:
                y_shifts = [1]
            elif j == (len(lines) - 1):
                y_shifts = [-1]
            else:
                y_shifts = [-1, 1]

            for x_shift in x_shifts:
                graph = add_neighbours(i, j, x_shift, 0, lines, graph)
            for y_shift in y_shifts:
                graph = add_neighbours(i, j, 0, y_shift, lines, graph)
    return graph, labyrinth, start_position


# This can be done way nicer with dict comprehension + itertools, but no time!
def get_key_paths(
    graph: Dict[Position, List[Position]],
    labyrinth: Labyrinth,
    start_position: Position,
) -> Dict[str, Dict[str, Optional[List[Position]]]]:
    key_paths = {}
    for outer_key, outer_pos in labyrinth.keys.items():
        key_paths[outer_key] = {}
        for inner_key, inner_pos in labyrinth.keys.items():
            print(outer_key, inner_key)
            if outer_key == inner_key:
                continue
            key_paths[outer_key][inner_key] = {}
            shortest_path = find_shortest_path(graph, outer_pos, inner_pos)
            key_paths[outer_key][inner_key]["path"] = shortest_path
            key_paths[outer_key][inner_key]["length"] = len(shortest_path) - 1

    key_paths["@"] = {}
    for inner_key, inner_pos in labyrinth.keys.items():
        key_paths["@"][inner_key] = {}
        shortest_path = find_shortest_path(graph, start_position, inner_pos)
        key_paths["@"][inner_key]["path"] = shortest_path
        key_paths["@"][inner_key]["length"] = len(shortest_path) - 1
        doors_blocking = {
            door_name
            for door_name, door_pos in labyrinth.doors.items()
            if door_pos in shortest_path
        }
        keys_blocking = {
            key_name
            for key_name, key_pos in labyrinth.keys.items()
            if key_pos in shortest_path
        }
        key_paths["@"][inner_key]["blocked_by"] = doors_blocking.union(
            keys_blocking
        ).difference({inner_key})
    return key_paths


def length_of_all_visits_1robot(
    current_key: str,
    available_keys: Set[str],
    keys_got: Set[str],
    visited,
    key_paths: Dict[str, Dict[str, Optional[List[Position]]]],
) -> int:
    lengths = []

    if len(available_keys) == 0:
        return 0
    for new_key in available_keys:
        new_keys_got = keys_got.union({new_key, new_key.upper()})
        unlocked_keys = {
            key_name
            for key_name, key_val in key_paths["@"].items()
            if key_val["blocked_by"].issubset(new_keys_got)
        }
        visited_key = "".join(sorted(new_keys_got)) + current_key + new_key
        if visited_key in visited.keys():
            length = visited[visited_key]
        else:
            length = key_paths[current_key][new_key][
                "length"
            ] + length_of_all_visits_1robot(
                new_key,
                available_keys.union(unlocked_keys).difference(new_keys_got),
                new_keys_got,
                visited,
                key_paths,
            )
            visited[visited_key] = length
        lengths.append(length)

    return min(lengths)


def length_of_all_visits_4robots(
    current_keys: Tuple[str, str, str, str],
    available_keys: Set[str],
    keys_got: Set[str],
    visited,
    key_paths: List[Dict[str, Dict[str, Optional[List[Position]]]]],
) -> int:
    lengths = []
    if len(available_keys) == 0:
        return 0
    for new_key in available_keys:
        robot = -1
        for i, (current_key, key_path) in enumerate(zip(current_keys, key_paths)):
            if current_key in key_path.keys():
                if new_key in key_path[current_key].keys():
                    robot = i
        new_keys_got = keys_got.union({new_key, new_key.upper()})
        unlocked_keys = set()
        for i in range(4):
            unlocked_keys = unlocked_keys.union(
                {
                    key_name
                    for key_name, key_val in key_paths[i]["@"].items()
                    if key_val["blocked_by"].issubset(new_keys_got)
                }
            )
        visited_key = "".join(sorted(new_keys_got)) + "".join(current_keys) + new_key
        if visited_key in visited.keys():
            length = visited[visited_key]
        else:
            length = key_paths[robot][current_keys[robot]][new_key][
                "length"
            ] + length_of_all_visits_4robots(
                [key if robot != i else new_key for i, key in enumerate(current_keys)],
                available_keys.union(unlocked_keys).difference(new_keys_got),
                new_keys_got,
                visited,
                key_paths,
            )
            visited[visited_key] = length
        lengths.append(length)

    return min(lengths)


def solve_1(puzzle_input: str):
    lines = puzzle_input.split()
    graph, lab, start = build_graph(lines)

    # Because I do not build the graph of they keys very smartly, it takes a while to build.
    # I did this once and then pickled the rest away
    # key_paths = get_key_paths(graph, labyrinth, start_position)
    # with open('day18_keypaths.pkl', 'wb') as handle:
    #    pickle.dump(key_paths, handle)
    # with open('day18_keypaths.pkl', 'rb') as handle:
    #    key_paths = pickle.load(handle)
    key_paths = get_key_paths(graph, lab, start)
    return length_of_all_visits_1robot(
        "@",
        {key for key in lab.keys.keys() if len(key_paths["@"][key]["blocked_by"]) == 0},
        set(),
        {},
        key_paths,
    )


def solve_2(puzzle_input: str):
    lines = puzzle_input.split()
    graph_1, lab_1, start_1 = build_graph(
        [line[: (len(line) // 2 + 1)] for line in lines[: (len(lines) // 2 + 1)]]
    )
    graph_2, lab_2, start_2 = build_graph(
        [line[(len(line) // 2) :] for line in lines[: (len(lines) // 2 + 1)]]
    )
    graph_3, lab_3, start_3 = build_graph(
        [line[: (len(line) // 2 + 1)] for line in lines[(len(lines) // 2) :]]
    )
    graph_4, lab_4, start_4 = build_graph(
        [line[(len(line) // 2) :] for line in lines[(len(lines) // 2) :]]
    )

    key_path_1 = get_key_paths(graph_1, lab_1, start_1)
    key_path_2 = get_key_paths(graph_2, lab_2, start_2)
    key_path_3 = get_key_paths(graph_3, lab_3, start_3)
    key_path_4 = get_key_paths(graph_4, lab_4, start_4)

    labs = [lab_1, lab_2, lab_3, lab_4]
    key_paths = [key_path_1, key_path_2, key_path_3, key_path_4]
    available_keys = set()
    for lab, key_path in zip(labs, key_paths):
        available_keys = available_keys.union(
            {
                key
                for key in lab.keys.keys()
                if len(key_path["@"][key]["blocked_by"]) == 0
            }
        )

    return length_of_all_visits_4robots(
        ["@", "@", "@", "@"], available_keys, set(), {}, key_paths
    )


if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    print("Result 1:", solve_1(puzzle_input))

    # For part 2, i modified the puzzle input by hand in the text file.
    # I basically did what is depicted in the puzzle description, adding 3@ and a few walls.
    # Part 2 will only run with that modification, part 1 will not run then anymore of course.
    # print("Result 2:", solve_2(puzzle_input))
