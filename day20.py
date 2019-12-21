import itertools
import heapq
import string
import sys
from typing import Dict, List, NamedTuple, Union

sys.setrecursionlimit(10 ** 6)

INF = float("Inf")


class Position(NamedTuple):
    x: int
    y: int


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


def other_name(name: str) -> str:
    if name in ["AA_o", "ZZ_o"]:
        return name
    if name[-1] == "i":
        return name[:3] + "o"
    else:
        return name[:3] + "i"


def other_name_lvl(name: str) -> str:
    if name in ["AA_o_0", "ZZ_o_0"]:
        return name
    level = name[5:]
    if name[3] == "i":
        return name[:3] + "o_" + str(int(level) + 1)
    else:
        return name[:3] + "i_" + str(int(level) - 1)


def dijkstra(graph, start: str, end: str) -> int:
    heap = []
    heapq.heappush(heap, (0, f"{start}_0"))
    end = f"{end}_0"
    costs = {f"{start}_0": 0}
    level = "0"
    while heap:
        if [heap_item[1] for heap_item in heap] == ["ZZ_o_0", "ZZ_o_0"]:
            portal_cost, portal_name = heapq.heappop(heap)
            costs[end] = portal_cost
            break
        portal_cost, portal_name = heapq.heappop(heap)
        level = portal_name[5:]

        for neighbour_name, neighbour_cost in graph[portal_name[:4]].items():
            neighbour_name = neighbour_name + f"_{level}"
            portaled_neighbour = other_name_lvl(neighbour_name)
            if (
                (neighbour_name[3] == "o")
                and (level == "0")
                and (neighbour_name[:2] != "ZZ")
            ):
                continue
            if (int(level) == 30) and (neighbour_name[3] == "i"):
                continue
            if (neighbour_name[:4]) == (other_name(portal_name[:4])):
                continue
            if (neighbour_name[:2] == "ZZ") and (neighbour_name[5:] != "0"):
                continue
            if (neighbour_name[:2] == "AA") and (neighbour_name[5:] != "0"):
                continue

            if neighbour_name in [heap_item[1] for heap_item in heap]:
                heap_cost = [
                    heap_item[0] for heap_item in heap if heap_item[1] == neighbour_name
                ][0]
                if portal_cost + neighbour_cost < costs.get(neighbour_name, INF) and (
                    portal_cost + neighbour_cost <= heap_cost
                ):
                    costs[neighbour_name] = portal_cost + neighbour_cost
                    costs[portaled_neighbour] = portal_cost + neighbour_cost
                    heap = [
                        heap_item
                        if heap_item[1] not in [neighbour_name, portaled_neighbour]
                        else (costs[neighbour_name], heap_item[1])
                        for heap_item in heap
                    ]
            elif neighbour_name not in costs.keys():
                costs[neighbour_name] = portal_cost + neighbour_cost
                costs[portaled_neighbour] = portal_cost + neighbour_cost
                heapq.heappush(heap, (portal_cost + neighbour_cost, neighbour_name))
                heapq.heappush(heap, (portal_cost + neighbour_cost, portaled_neighbour))
    return costs


def find_portal_letter(i: int, j: int, lines: List[str]) -> str:
    if i == 0:
        x_shifts = [1]
    elif i == (len(lines[0]) - 1):
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
        current_neighbour = lines[j][i + x_shift]
        if current_neighbour in string.ascii_uppercase:
            return current_neighbour
    for y_shift in y_shifts:
        current_neighbour = lines[j + y_shift][i]
        if current_neighbour in string.ascii_uppercase:
            return current_neighbour
    raise ValueError("No portal found.")


def find_portal_letter_link(i: int, j: int, lines: List[str]) -> (bool, int, int):
    if i == 0:
        x_shifts = [1]
    elif i == (len(lines[0]) - 1):
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
        if lines[j][i + x_shift] == ".":
            return True, x_shift, 0
    for y_shift in y_shifts:
        if lines[j + y_shift][i] == ".":
            return True, 0, y_shift
    return False, 0, 0


def add_neighbours(
    i: int,
    j: int,
    x_shift: int,
    y_shift: int,
    lines: List[str],
    graph: Dict[Position, List[Position]],
    portals: Dict[str, List[Position]],
    use_portals: bool,
):
    current_neighbour = lines[j + y_shift][i + x_shift]
    current_position = Position(x=i + x_shift, y=j + y_shift)
    if current_neighbour == ".":
        graph[Position(x=i, y=j)].append(current_position)

    if use_portals:
        if current_neighbour in string.ascii_uppercase:
            second_letter = find_portal_letter(i + x_shift, j + y_shift, lines)
            portal_key = "".join(sorted(current_neighbour + second_letter))
            for pos in portals[portal_key]:
                graph[Position(x=i, y=j)].append(pos)
    return graph


def find_portals(lines: List[str]) -> Dict[str, List[Position]]:
    portals = {}
    for j, line in enumerate(lines):
        for i, pixel in enumerate(line):
            if pixel in [" ", "#", "."]:
                continue
            portal_letter = find_portal_letter(i, j, lines)
            portal_key = "".join(sorted(pixel + portal_letter))
            found, x_shift, y_shift = find_portal_letter_link(i, j, lines)
            if found:
                if portal_key in portals.keys():
                    portals[portal_key].append(Position(x=i + x_shift, y=j + y_shift))
                else:
                    portals[portal_key] = [Position(x=i + x_shift, y=j + y_shift)]
    return portals


def build_graph(
    lines: List[str], use_portals: bool = True
) -> (Dict[Position, List[Position]], Dict[str, List[Position]]):
    graph = {}
    portals = find_portals(lines)
    for j, line in enumerate(lines):
        for i, pixel in enumerate(line):
            if pixel in [" ", "#"]:
                continue
            if not use_portals:
                if pixel in string.ascii_uppercase:
                    continue
            graph[Position(x=i, y=j)] = []

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
                graph = add_neighbours(
                    i, j, x_shift, 0, lines, graph, portals, use_portals
                )
            for y_shift in y_shifts:
                graph = add_neighbours(
                    i, j, 0, y_shift, lines, graph, portals, use_portals
                )
    return graph, portals


def build_portal_graph(
    graph: Dict[Position, List[Position]], portals_oi: Dict[str, Position]
) -> Dict[str, Dict[str, Union[str, int]]]:
    portal_graph = {}
    for start_name, start_position in portals_oi.items():
        portal_graph[start_name] = {}
        for end_name, end_position in portals_oi.items():
            if start_name == end_name:
                continue
            if start_name[:2] == end_name[:2]:
                portal_graph[start_name][end_name] = 0
                continue
            path = find_shortest_path(graph, start_position, end_position)
            if not path is None:
                portal_graph[start_name][end_name] = len(path)
    return portal_graph


def solve_1(puzzle_input: str) -> int:
    lines = puzzle_input.splitlines()
    max_line_length = max([len(line) for line in lines])
    lines = [line.ljust(max_line_length) for line in lines]

    graph, portals, = build_graph(lines)
    start_position = portals["AA"][0]
    end_position = portals["ZZ"][0]
    path = find_shortest_path(graph, start_position, end_position)
    return len(path) - 1  # Account for starting in Portal "AA", not in front of it


def solve_2(puzzle_input: str) -> int:
    lines = puzzle_input.splitlines()
    max_line_length = max([len(line) for line in lines])
    lines = [line.ljust(max_line_length) for line in lines]

    graph, portals, = build_graph(lines, use_portals=False)
    portals_oi = {}
    for name, positions in portals.items():
        for position in positions:
            if (
                (position.y == 2)
                or (position.x == 2)
                or (position.y == len(lines) - 3 or (position.x == max_line_length - 3))
            ):
                portals_oi[f"{name}_o"] = position
            else:
                portals_oi[f"{name}_i"] = position

    portal_graph = build_portal_graph(graph, portals_oi)
    costs = dijkstra(portal_graph, "AA_o", "ZZ_o")
    return costs["ZZ_o_0"] - 1


if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    print("Result 1:", solve_1(puzzle_input))
    print("Result 2:", solve_2(puzzle_input))
