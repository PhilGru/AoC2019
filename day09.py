import itertools
import sys
from typing import List, NamedTuple

#################### INTCODE COMPUTER ############################
valid_opcodes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 99]

mode_lengths = {1: 3, 2: 3, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 3, 9: 1, 99: 0}


class Program:
    def __init__(
        self,
        array: List[int],
        pointer: int,
        inputs: List[int],
        relative_base: int,
        extra_memory: int,
    ):
        self.array = array + [0] * extra_memory
        self.pointer = pointer
        self.inputs = inputs
        self.output = []
        self.relative_base = relative_base


def parse_modes(value: int) -> (int, List[int]):
    opcode = int(str(value)[-2:])
    modes = [int(val) for val in str(value)[:-2]]
    for i in range(mode_lengths[opcode] - len(modes)):
        modes.insert(0, 0)
    return opcode, modes[::-1]


def use_mode(array: List[int], pointer: int, relative_base: int, mode: int) -> int:
    if mode == 0:
        return array[array[pointer]]
    elif mode == 1:
        return array[pointer]
    elif mode == 2:
        return array[array[pointer] + relative_base]
    else:
        raise ValueError(f"Wrong mode {modes[0]}")


def use_mode_insertion(
    program: Program, pointer_offset: int, value: int, mode: int
) -> int:
    pointer, array, relative_base = (
        program.pointer,
        program.array,
        program.relative_base,
    )
    if mode == 0:
        program.array[array[pointer + pointer_offset]] = value
        return program
    elif mode == 1:
        raise ValueError("I don't think mode 1 in opcode 3 is valid?")
    elif mode == 2:
        program.array[array[pointer + pointer_offset] + relative_base] = value
        return program
    else:
        raise ValueError(f"Wrong mode {modes[0]}")


def opcode_1(program: Program, modes: List[int]) -> Program:
    pointer, array, relative_base = (
        program.pointer,
        program.array,
        program.relative_base,
    )
    first_param = use_mode(array, pointer + 1, relative_base, modes[0])
    second_param = use_mode(array, pointer + 2, relative_base, modes[1])
    result_sum = first_param + second_param
    program = use_mode_insertion(program, 3, result_sum, modes[2])
    program.pointer = pointer + 4
    return program


def opcode_2(program: Program, modes: List[int]) -> Program:
    pointer, array, relative_base = (
        program.pointer,
        program.array,
        program.relative_base,
    )
    first_param = use_mode(array, pointer + 1, relative_base, modes[0])
    second_param = use_mode(array, pointer + 2, relative_base, modes[1])
    result_sum = first_param * second_param
    program = use_mode_insertion(program, 3, result_sum, modes[2])
    program.pointer = pointer + 4
    return program


def opcode_3(program: Program, modes: List[int]) -> Program:
    pointer, array, relative_base = (
        program.pointer,
        program.array,
        program.relative_base,
    )
    current_input = program.inputs.pop(0)
    program = use_mode_insertion(program, 1, current_input, modes[0])
    program.pointer = program.pointer + 2
    return program


def opcode_4(program: Program, modes: List[int]) -> Program:
    pointer, array, relative_base = (
        program.pointer,
        program.array,
        program.relative_base,
    )
    param = use_mode(array, pointer + 1, relative_base, modes[0])
    program.output.append(param)
    program.pointer = pointer + 2
    return program


def opcode_5(program: Program, modes: List[int]) -> Program:
    pointer, array, relative_base = (
        program.pointer,
        program.array,
        program.relative_base,
    )
    first_param = use_mode(array, pointer + 1, relative_base, modes[0])
    second_param = use_mode(array, pointer + 2, relative_base, modes[1])
    if first_param != 0:
        program.pointer = second_param
    else:
        program.pointer = pointer + 3
    return program


def opcode_6(program: Program, modes: List[int]) -> Program:
    pointer, array, relative_base = (
        program.pointer,
        program.array,
        program.relative_base,
    )
    first_param = use_mode(array, pointer + 1, relative_base, modes[0])
    second_param = use_mode(array, pointer + 2, relative_base, modes[1])
    if first_param == 0:
        program.pointer = second_param
    else:
        program.pointer = pointer + 3
    return program


def opcode_7(program: Program, modes: List[int]) -> Program:
    pointer, array, relative_base = (
        program.pointer,
        program.array,
        program.relative_base,
    )
    first_param = use_mode(array, pointer + 1, relative_base, modes[0])
    second_param = use_mode(array, pointer + 2, relative_base, modes[1])
    if first_param < second_param:
        program = use_mode_insertion(program, 3, 1, modes[2])
    else:
        program = use_mode_insertion(program, 3, 0, modes[2])
    program.pointer = pointer + 4
    return program


def opcode_8(program: Program, modes: List[int]) -> Program:
    pointer, array, relative_base = (
        program.pointer,
        program.array,
        program.relative_base,
    )
    first_param = use_mode(array, pointer + 1, relative_base, modes[0])
    second_param = use_mode(array, pointer + 2, relative_base, modes[1])
    if first_param == second_param:
        program = use_mode_insertion(program, 3, 1, modes[2])
    else:
        program = use_mode_insertion(program, 3, 0, modes[2])
    program.pointer = pointer + 4
    return program


def opcode_9(program: Program, modes: List[int]) -> Program:
    pointer, array, relative_base = (
        program.pointer,
        program.array,
        program.relative_base,
    )
    param = use_mode(array, pointer + 1, relative_base, modes[0])
    program.relative_base = relative_base + param
    program.pointer = pointer + 2
    return program


def opcode_99(program: Program, modes: List[int]) -> Program:
    return program


opcode_functions = {
    1: opcode_1,
    2: opcode_2,
    3: opcode_3,
    4: opcode_4,
    5: opcode_5,
    6: opcode_6,
    7: opcode_7,
    8: opcode_8,
    9: opcode_9,
    99: opcode_99,
}


def do_step(program: Program) -> (Program, bool):
    opcode, modes = parse_modes(program.array[program.pointer])
    if opcode not in valid_opcodes:
        raise ValueError(f"Invalid opcode {opcode}")
    new_program = opcode_functions[opcode](program, modes)
    return new_program, opcode


def initiate_program(
    puzzle_input: List[int], input_list: List[int], extra_memory=10000
) -> Program:
    return Program(
        array=puzzle_input,
        pointer=0,
        inputs=input_list,
        relative_base=0,
        extra_memory=extra_memory,
    )


####################################################################


def run_program(puzzle_input: List[int], input_list: List[int]) -> Program:
    program = initiate_program(puzzle_input, input_list)
    last_step = 0
    while last_step != 99:
        program, last_step = do_step(program)
    return program


if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    puzzle_input = [int(x) for x in puzzle_input.split(",")]
    print("Result 1:", run_program(puzzle_input, [1]).output)
    print("Result 2:", run_program(puzzle_input, [2]).output)