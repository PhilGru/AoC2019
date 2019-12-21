import itertools
import sys
from typing import List, NamedTuple

#################### INTCODE COMPUTER ############################
valid_opcodes = [1, 2, 3, 4, 5, 6, 7, 8, 99]


class Program:
    def __init__(self, array: List[int], pointer: int, inputs: List[int]):
        self.array = array
        self.pointer = pointer
        self.inputs = inputs
        self.output = []


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
    program.array[array[pointer + 3]] = result_sum
    program.pointer = pointer + 4
    return program


def opcode_2(program: Program, modes: List[int]) -> Program:
    pointer = program.pointer
    array = program.array
    first_param = use_mode(array, pointer + 1, modes[0])
    second_param = use_mode(array, pointer + 2, modes[1])
    result_sum = first_param * second_param
    program.array[array[pointer + 3]] = result_sum
    program.pointer = pointer + 4
    return program


def opcode_3(program: Program) -> Program:
    pointer = program.pointer
    array = program.array
    current_input = program.inputs.pop(0)
    program.array[array[pointer + 1]] = current_input
    program.pointer = program.pointer + 2
    return program


def opcode_4(program: Program, modes: List[int]) -> Program:
    pointer = program.pointer
    array = program.array
    param = use_mode(array, pointer + 1, modes[0])
    program.output.append(param)
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
        return new_program, opcode
    if opcode == 2:
        new_program = opcode_2(program, modes)
        return new_program, opcode
    if opcode == 3:
        new_program = opcode_3(program)
        return new_program, opcode
    if opcode == 4:
        new_program = opcode_4(program, modes)
        return new_program, opcode
    if opcode == 5:
        new_program = opcode_5(program, modes)
        return new_program, opcode
    if opcode == 6:
        new_program = opcode_6(program, modes)
        return new_program, opcode
    if opcode == 7:
        new_program = opcode_7(program, modes)
        return new_program, opcode
    if opcode == 8:
        new_program = opcode_8(program, modes)
        return new_program, opcode
    if opcode == 99:
        new_program = opcode_99(program)
        return new_program, opcode


def initiate_program(puzzle_input: List[int], input_list: List[int]) -> Program:
    return Program(array=puzzle_input, pointer=0, inputs=input_list)


####################################################################


def run_program(puzzle_input: List[int], input_list: List[int]) -> Program:
    program = initiate_program(puzzle_input, input_list)
    last_step = 0
    while last_step != 99:
        program, last_step = do_step(program)
    return program


def continue_program_till_output_or_halt(program: Program, last_step: int) -> Program:
    if last_step != 99:
        last_step = 0
    while (last_step != 4) and (last_step != 99):
        program, last_step = do_step(program)
    return program, last_step


def calculate_thrusting_no_feedback(
    puzzle_input: List[int], sequence: List[int]
) -> int:
    output_amp = 0
    for seq in sequence:
        program = run_program(puzzle_input, [seq, output_amp])
        output_amp = program.output[0]
    return output_amp


def get_max_thrusting_part1(puzzle_input: List[int]) -> int:
    return max(
        [
            calculate_thrusting_no_feedback(puzzle_input, list(perm))
            for perm in itertools.permutations([0, 1, 2, 3, 4])
        ]
    )


def calculate_thrusting_feedback(puzzle_input: List[int], sequence: List[int]) -> int:
    thrustings = []
    for seq in sequence:
        amp_a = initiate_program(puzzle_input, [seq[0], 0])
        amp_b = initiate_program(puzzle_input, [seq[1]])
        amp_c = initiate_program(puzzle_input, [seq[2]])
        amp_d = initiate_program(puzzle_input, [seq[3]])
        amp_e = initiate_program(puzzle_input, [seq[4]])
        amps = [amp_a, amp_b, amp_c, amp_d, amp_e]
        last_steps = [0, 0, 0, 0, 0]
        connections = [1, 2, 3, 4, 0]

        i = 0
        current_amp = 0
        all_halt = False
        while not all_halt:
            (
                amps[current_amp],
                last_steps[current_amp],
            ) = continue_program_till_output_or_halt(
                amps[current_amp], last_steps[current_amp]
            )
            amps[connections[current_amp]].inputs.append(amps[current_amp].output[-1])
            all_halt = all([last_step == 99 for last_step in last_steps])

            current_amp = connections[current_amp]
        thrustings.append(amps[4].output[-1])
    return thrustings


def get_max_thrusting_part2(puzzle_input: List[int]) -> int:
    perms = itertools.permutations([5, 6, 7, 8, 9])
    thrustings = calculate_thrusting_feedback(puzzle_input, list(perms))
    return max(thrustings)


if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    puzzle_input = [int(x) for x in puzzle_input.split(",")]
    print("Result 1:", get_max_thrusting_part1(puzzle_input))
    print("Result 2:", get_max_thrusting_part2(puzzle_input))
