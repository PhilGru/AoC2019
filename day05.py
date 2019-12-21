import sys
from typing import List, NamedTuple

#################### INTCODE COMPUTER ############################
valid_opcodes = [1, 2, 3, 4, 5, 6, 7, 8, 99]


class Program:
    def __init__(self, array: List[int], pointer: int):
        self.array = array
        self.pointer = pointer
        self.output = []

    def change_value(self, position: int, new_value: int) -> None:
        self.array[position] = new_value


mode_lengths = {1: 3, 2: 3, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 3, 99: 0}


def parse_modes(value: int) -> (int, List[int]):
    opcode = int(str(value)[-2:])
    modes = [int(val) for val in str(value)[:-2]]
    for i in range(mode_lengths[opcode] - len(modes)):
        modes.insert(0, 0)
    return opcode, modes[::-1]


def use_mode(array: List[int], pointer: int, mode: int) -> int:
    if mode == 0:
        return array[array[pointer]]
    elif mode == 1:
        return array[pointer]
    else:
        raise ValueError(f"Wrong mode {modes[0]}")


def opcode_1(program: Program, modes: List[int]) -> Program:
    pointer = program.pointer
    array = program.array
    first_param = use_mode(array, pointer + 1, modes[0])
    second_param = use_mode(array, pointer + 2, modes[1])
    result_sum = first_param + second_param
    program.change_value(array[pointer + 3], result_sum)
    program.pointer = pointer + 4
    return program


def opcode_2(program: Program, modes: List[int]) -> Program:
    pointer = program.pointer
    array = program.array
    first_param = use_mode(array, pointer + 1, modes[0])
    second_param = use_mode(array, pointer + 2, modes[1])
    result_sum = first_param * second_param
    program.change_value(array[pointer + 3], result_sum)
    program.pointer = pointer + 4
    return program


def opcode_3(program: Program) -> Program:  # Too lazy to do inputes correctly
    program.pointer = program.pointer + 2
    return program


def opcode_4(program: Program, modes: List[int]) -> Program:
    pointer = program.pointer
    array = program.array
    param = use_mode(array, pointer + 1, modes[0])
    program.output.append(array[array[pointer + 1]])
    program.pointer = pointer + 2
    return program


def opcode_5(program: Program, modes: List[int]) -> Program:
    pointer = program.pointer
    array = program.array
    first_param = use_mode(array, pointer + 1, modes[0])
    second_param = use_mode(array, pointer + 2, modes[1])
    if first_param != 0:
        program.pointer = second_param
    else:
        program.pointer = pointer + 3
    return program


def opcode_6(program: Program, modes: List[int]) -> Program:
    pointer = program.pointer
    array = program.array
    first_param = use_mode(array, pointer + 1, modes[0])
    second_param = use_mode(array, pointer + 2, modes[1])
    if first_param == 0:
        program.pointer = second_param
    else:
        program.pointer = pointer + 3
    return program


def opcode_7(program: Program, modes: List[int]) -> Program:
    pointer = program.pointer
    array = program.array
    first_param = use_mode(array, pointer + 1, modes[0])
    second_param = use_mode(array, pointer + 2, modes[1])
    if first_param < second_param:
        program.array[array[pointer + 3]] = 1
    else:
        program.array[array[pointer + 3]] = 0
    program.pointer = pointer + 4
    return program


def opcode_8(program: Program, modes: List[int]) -> Program:
    pointer = program.pointer
    array = program.array
    first_param = use_mode(array, pointer + 1, modes[0])
    second_param = use_mode(array, pointer + 2, modes[1])
    if first_param == second_param:
        program.array[array[pointer + 3]] = 1
    else:
        program.array[array[pointer + 3]] = 0
    program.pointer = pointer + 4
    return program


def opcode_99(program: Program) -> Program:
    return program


def initiate_program(input_array: List[int]) -> Program:
    return Program(array=input_array, pointer=0)


def do_step(program: Program) -> (Program, bool):
    opcode, modes = parse_modes(program.array[program.pointer])
    if opcode not in valid_opcodes:
        print(
            program.pointer,
            program.array,
            program.array[program.pointer - 5 : program.pointer + 5],
        )
        raise ValueError(f"Invalid opcode {opcode}")
    if opcode == 1:
        new_program = opcode_1(program, modes)
        return new_program, True
    if opcode == 2:
        new_program = opcode_2(program, modes)
        return new_program, True
    if opcode == 3:
        new_program = opcode_3(program)
        return new_program, True
    if opcode == 4:
        new_program = opcode_4(program, modes)
        return new_program, True
    if opcode == 5:
        new_program = opcode_5(program, modes)
        return new_program, True
    if opcode == 6:
        new_program = opcode_6(program, modes)
        return new_program, True
    if opcode == 7:
        new_program = opcode_7(program, modes)
        return new_program, True
    if opcode == 8:
        new_program = opcode_8(program, modes)
        return new_program, True
    if opcode == 99:
        new_program = opcode_99(program)
        return new_program, False


####################################################################


def run_program(puzzle_input: List[int]) -> Program:
    program = initiate_program(puzzle_input)
    keep_running = True
    while keep_running:
        program, keep_running = do_step(program)
    return program


if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    puzzle_input = [int(x) for x in puzzle_input.split(",")]
    puzzle_input_1 = [digit for digit in puzzle_input]
    puzzle_input_1[225] = 1  # Harcoded opcode 3
    result_program = run_program(puzzle_input_1)
    print("Result 1:", result_program.output[-1])

    puzzle_input[225] = 5  # Harcoded opcode 3
    result_program = run_program(puzzle_input)
    print("Result 2:", result_program.output[-1])
