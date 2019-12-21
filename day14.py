from collections import defaultdict
import sys
from typing import Dict, NewType, List, Union

Reactions = NewType("Reactions", Dict[str, Dict[str, Union[int, Dict[str, int]]]])


def parse_input(puzzle_input: str) -> Reactions:
    reactions = {}
    for line in puzzle_input.split("\n"):
        split_line = line.split("=>")

        output_chem = split_line[1].strip().split(" ")[1]
        output_count = int(split_line[1].strip().split(" ")[0])
        reactions[output_chem] = {"count": output_count}

        reactions[output_chem]["elements"] = {}
        input_chem_counts = split_line[0].split(",")
        for chem_count in input_chem_counts:
            input_chem = chem_count.strip().split(" ")[1]
            input_count = int(chem_count.strip().split(" ")[0])
            reactions[output_chem]["elements"][input_chem] = input_count

    reactions["START"] = {"count": 1, "elements": {"FUEL": 1}}
    return reactions


def reactions_from_storage(
    chem: str, count: int, storage, reactions: Reactions
) -> (int, int):
    raw_reaction_count = count // reactions[chem]["count"]
    if count % reactions[chem]["count"] != 0:
        raw_reaction_count += 1
    possible_reactions_from_storage = min(
        [storage[key] // val for key, val in reactions[chem]["elements"].items()]
    )
    return (
        raw_reaction_count,
        min(raw_reaction_count, possible_reactions_from_storage),
    )  # how many reactions do i need and how many can i do from storage


def need(reactions: Reactions, storage: defaultdict) -> (Dict[str, int], defaultdict):
    needed = {"START": 1}
    done = False
    while not done:
        for need_chem in list(needed.keys()):
            if need_chem == "ORE":
                continue
            need_count = needed[need_chem]
            reactions_needed, reactions_storage = reactions_from_storage(
                need_chem, need_count, storage, reactions
            )
            produced_count = reactions[need_chem]["count"] * (
                reactions_needed - reactions_storage
            )
            storage[need_chem] = storage[need_chem] + max(
                0, produced_count - need_count
            )

            for reaction_chem, reaction_count in reactions[need_chem][
                "elements"
            ].items():
                # Do reactions from storage
                current_storage = storage[reaction_chem]
                storage[reaction_chem] = current_storage - (
                    reactions_storage * reaction_count
                )
                if storage[reaction_chem] < 0:
                    raise ValueError("Nope")

                # Add new elements that aren't in storage to need list
                needed_reaction_chem_count = reaction_count * (
                    reactions_needed - reactions_storage
                )
                current_needed = needed.get(reaction_chem, 0)
                needed[reaction_chem] = current_needed + max(
                    0, needed_reaction_chem_count - storage[reaction_chem]
                )
                storage[reaction_chem] = max(
                    0, storage[reaction_chem] - needed_reaction_chem_count
                )
                if storage[reaction_chem] < 0:
                    raise ValueError("Also nope")

            needed.pop(need_chem)

        if list(needed.keys()) == ["ORE"]:
            done = True
    return needed, storage


def solve_1(puzzle_input: str) -> int:
    parsed = parse_input(puzzle_input)
    storage = defaultdict(int)
    return need(parsed, storage)[0]["ORE"]


def get_ore(last_chem: str, chem: str, reactions: Reactions) -> int:
    if chem == "ORE":
        return 1
    ore = 0
    for reaction_chem, reaction_val in reactions[chem]["elements"].items():
        ore = ore + (
            (reaction_val / reactions[chem]["count"])
            * get_ore(chem, reaction_chem, reactions)
        )
    return ore


def solve_2(puzzle_input: str) -> (int, int):
    parsed = parse_input(puzzle_input)
    return get_ore("X", "FUEL", parsed)


if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    print("Result 1:", solve_1(puzzle_input))
    # Interestingly, don't need part 1 for part 2.
    # Get perfect ore for 1 fuel, then divide 1 trillion by that number.
    # This works for large numbers, because every excess will be used.
    # The excess at large fuels will just be some decimal digits we can truncate.
    ore_for_one_fuel_no_excess = solve_2(puzzle_input)
    print("Result 2:", int(1e12 / ore_for_one_fuel_no_excess))
