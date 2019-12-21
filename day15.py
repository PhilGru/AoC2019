import itertools
import os
import pickle
import random
import sys
from enum import IntEnum
from typing import Any, Dict, List, NamedTuple, NewType, Set

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
    if (opcode == 3) and (program.inputs == []):
        return program, -1
    new_program = opcode_functions[opcode](program, modes)
    return new_program, opcode


def initiate_program(
    puzzle_input: List[int], input_list: List[int], extra_memory: int = 10000
) -> Program:
    return Program(
        array=puzzle_input,
        pointer=0,
        inputs=input_list,
        relative_base=0,
        extra_memory=extra_memory,
    )


def continue_program_till_no_input_or_halt(
    program: Program, last_step: int
) -> (Program, int):
    if last_step != 99:
        last_step = 0
    while (last_step != -1) and (last_step != 99):
        program, last_step = do_step(program)
    return program, last_step


####################################################################


class Direction(IntEnum):
    north = 1
    south = 2
    west = 3
    east = 4


class Position(NamedTuple):
    x: int
    y: int


def reverse_direction(direction: Direction) -> Direction:
    if direction == Direction.north:
        return Direction.south
    if direction == Direction.south:
        return Direction.north
    if direction == Direction.west:
        return Direction.east
    if direction == Direction.east:
        return Direction.west


def get_move(direction: Direction) -> (int, int):
    if direction == Direction.north:
        return 0, -1
    if direction == Direction.south:
        return 0, 1
    if direction == Direction.west:
        return 1, 0
    if direction == Direction.east:
        return -1, 0


def move_direction(position: Position, direction: Direction) -> Position:
    x_move, y_move = get_move(direction)
    return Position(position.x + x_move, position.y + y_move)


Board = NewType("Board", Dict[Position, int])


def print_board(board: Board) -> None:
    picture = []
    for i in range(-30, 20):
        row = []
        for j in range(-20, 30):
            if Position(x=j, y=i) in board.keys():
                if board[Position(x=j, y=i)] == 0:
                    row.append("#")
                if board[Position(x=j, y=i)] == 1:
                    row.append(".")
                if board[Position(x=j, y=i)] == 2:
                    row.append("X")
            else:
                row.append("█")
        picture.append("".join(row))
    for col in picture:
        print(col)


def discover(
    position: Position, board: Board, program: Program, last_step: int
) -> (Board, Program, int):
    for direction in Direction:
        new_position = move_direction(position, direction)
        if new_position not in board.keys():
            program.inputs.append(direction)
            program, last_step = continue_program_till_no_input_or_halt(
                program, last_step
            )
            discovered = program.output[-1]
            board[new_position] = discovered
            if discovered != 0:
                program.inputs.append(reverse_direction(direction))
                program, last_step = continue_program_till_no_input_or_halt(
                    program, last_step
                )
    return board, program, last_step


def solve_1(puzzle_input: List[int]) -> Board:
    program = initiate_program(puzzle_input, [])
    done = False
    position = Position(x=0, y=0)
    last_step = 0
    board = {}
    random_walk_nr_steps = 1000000
    for i in range(random_walk_nr_steps):
        if i % 10000 == 0:
            print(f"Random Walk Step {i} of {random_walk_nr_steps}.")
        board, program, last_step = discover(position, board, program, last_step)
        possible_next = []
        for direction in Direction:
            new_position = move_direction(position, direction)
            if board[new_position] != 0:
                possible_next.append(direction)
        next_direction = random.choice(possible_next)
        position = move_direction(position, next_direction)
        program.inputs.append(next_direction)
        program, last_step = continue_program_till_no_input_or_halt(program, last_step)
    board[Position(x=0, y=0)] = 2
    print_board(board)
    return board


def expand_oxygen(oxygened: Set[Position], board: Board) -> Set[Position]:
    positions = list(oxygened)
    for oxygen in positions:
        for direction in Direction:
            new_position = move_direction(oxygen, direction)
            if board[new_position] != 0:
                oxygened.add(new_position)
    return oxygened


def print_board_oxy(board: Board, oxygened: Set[Position]) -> None:
    picture = []
    for i in range(-30, 20):
        row = []
        for j in range(-20, 30):
            if Position(x=j, y=i) in board.keys():
                if Position(x=j, y=i) in oxygened:
                    row.append("O")
                elif board[Position(x=j, y=i)] == 0:
                    row.append("#")
                elif board[Position(x=j, y=i)] == 1:
                    row.append(".")
                elif board[Position(x=j, y=i)] == 2:
                    row.append("X")
            else:
                row.append("█")
        picture.append("".join(row))
    for col in picture:
        print(col)


def solve_2(board: Board):
    X_positions = [key for key, val in board.items() if val == 2]
    X_positions.remove(Position(x=0, y=0))
    start_position = X_positions[0]
    oxygened = {start_position}

    done = False
    i = 0
    while not done:
        old_oxygened = oxygened.copy()
        oxygened = expand_oxygen(oxygened, board)
        if oxygened == old_oxygened:
            done = True
        else:
            i += 1
            # os.system('cls')
        # print_board_oxy(board, oxygened)
    return i


if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    puzzle_input = [int(x) for x in puzzle_input.split(",")]

    # Use random walk for part 1, with 1 million steps.
    # Because this takes long, we save the board for part 2.
    board = solve_1(puzzle_input)
    # with open('day15_board.pkl', 'wb') as handle:
    #    pickle.dump(board, handle)

    # with open('day15_board.pkl', 'rb') as handle:
    #    board = pickle.load(handle)

    print("Result 2:", solve_2(board))
