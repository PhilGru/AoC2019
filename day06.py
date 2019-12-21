import sys
from typing import Dict, List, Set


def parse_input_1(input_list: List[str]) -> Dict[str, str]:
    orbits = {}
    for inp in input_list:
        inp_val, inp_key = inp.split(")")
        if inp_key in orbits.keys():
            orbits[inp_key].append(inp_val)
        else:
            orbits[inp_key] = [inp_val]
    return orbits


def parse_input_2(input_list: List[str]) -> Dict[str, str]:
    orbits = {}
    for inp in input_list:
        inp_key, inp_val = inp.split(")")
        if inp_key in orbits.keys():
            orbits[inp_key].append(inp_val)
        else:
            orbits[inp_key] = [inp_val]

    for inp in input_list:
        inp_val, inp_key = inp.split(")")
        if inp_key in orbits.keys():
            orbits[inp_key].append(inp_val)
        else:
            orbits[inp_key] = [inp_val]
    return orbits


def update_orbits(orbits: Dict[str, str], planet: str, count: int) -> Dict[str, str]:
    for key, value in orbits.items():
        if planet in value:
            new_value = value.copy()
            new_value.remove(planet)
            new_value.append(count)
            orbits[key] = new_value
            if all([isinstance(val, int) for val in orbits[key]]):
                update_orbits(orbits, key, sum(orbits[key]) + len(orbits[key]))
    return orbits


def move_further(
    orbits: Dict[str, str], planet: str, count: int, planets_visited: Set[str]
):
    if planet in planets_visited:  # Preventing endless loop
        return [float("Inf")]
    if planet not in orbits.keys():  # Dead end
        return [float("Inf")]
    if planet == "SAN":
        return [count]

    ress = []
    for plan in orbits[planet]:
        new_planets_visited = planets_visited.copy()
        new_planets_visited.add(planet)
        ress.extend(move_further(orbits, plan, count + 1, new_planets_visited))
    return ress


def solve_1(puzzle_input: List[str]) -> int:
    parsed = parse_input_1(puzzle_input)
    orbits = update_orbits(parsed, "COM", 0)
    total_sum = 0
    for val in orbits.values():
        total_sum += sum(val)
    return total_sum + len(orbits.keys())


def solve_2(puzzle_input: List[str]) -> int:
    parsed = parse_input_2(puzzle_input)
    res = move_further(parsed, "YOU", 0, set())
    return min(res) - 2  # Removing "YOU" and "SAN" from sum


if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    puzzle_input = puzzle_input.split()
    print("Result 1:", solve_1(puzzle_input))
    print("Result 2:", solve_2(puzzle_input))
