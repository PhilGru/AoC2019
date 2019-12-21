import sys
from typing import List


valid_opcodes = [1, 2, 99]


class Program:
    def __init__(self, array: List[int], pointer: int):
        self.array = array
        self.pointer = pointer

    def change_value(self, position: int, new_value: int) -> None:
        self.array[position] = new_value


def opcode_1(program: Program) -> Program:
    pointer = program.pointer
    array = program.array
    result_sum = array[array[pointer + 1]] + array[array[pointer + 2]]
    program.change_value(array[pointer + 3], result_sum)
    program.pointer = pointer + 4
    return program


def opcode_2(program: Program) -> Program:
    pointer = program.pointer
    array = program.array
    result_sum = array[array[pointer + 1]] * array[array[pointer + 2]]
    program.change_value(array[pointer + 3], result_sum)
    program.pointer = pointer + 4
    return program


def opcode_99(program: Program) -> Program:
    return program


def initiate_program(input_array: List[int]) -> Program:
    return Program(array=input_array, pointer=0)


def do_step(program: Program) -> (Program, bool):
    opcode = program.array[program.pointer]
    if opcode not in valid_opcodes:
        raise ValueError(f"Invalid opcode {opcode}")
    if opcode == 1:
        new_program = opcode_1(program)
        return new_program, True
    if opcode == 2:
        new_program = opcode_2(program)
        return new_program, True
    if opcode == 99:
        new_program = opcode_99(program)
        return new_program, False


def run_program(puzzle_input: List[int]) -> Program:
    program = initiate_program(puzzle_input)
    keep_running = True
    while keep_running:
        program, keep_running = do_step(program)
    return program


def check_for_specific_output(puzzle_input=List[int]) -> Program:
    for noun in range(100):
        for verb in range(100):
            new_puzzle_input = puzzle_input.copy()
            new_puzzle_input[1] = noun
            new_puzzle_input[2] = verb
            new_program = run_program(new_puzzle_input)
            if new_program.array[0] == 19690720:
                return noun, verb


if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    puzzle_input = [int(x) for x in puzzle_input.split(",")]
    puzzle_input_1 = [digit for digit in puzzle_input]
    puzzle_input_1[1] = 12
    puzzle_input_1[2] = 2
    result_program = run_program(puzzle_input_1)
    print("Result 1: ", result_program.array[0])
    noun, verb = check_for_specific_output(puzzle_input)
    print("Result 2: ", 100 * noun + verb)
