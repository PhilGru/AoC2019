import itertools
import os
import sys
from enum import IntEnum
from typing import Any, Dict, List, NamedTuple, NewType, Set, Tuple

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


class Position(NamedTuple):
    x: int
    y: int


def print_board(board: Dict[Position, str]) -> None:
    picture = []
    for i in range(0, 60):
        row = []
        for j in range(0, 60):
            row.append(board.get(Position(x=j, y=i), ""))
        picture.append("".join(row))
    for col in picture:
        print(col)


def transform_board(program_output: List[int]) -> Dict[Position, str]:
    board = {}
    curr_row = 0
    for col, val in enumerate(program_output):
        if val == 10:
            curr_row += 1
            board[Position(x=(col % 56), y=curr_row)] = "█"
        else:
            board[Position(x=(col % 56), y=curr_row)] = chr(val)
    return board


def is_crossing(position: Position, board: Dict[Position, str]) -> bool:
    return (
        (board.get(Position(x=position.x + 1, y=position.y)) == "#")
        and (board.get(Position(x=position.x - 1, y=position.y)) == "#")
        and (board.get(Position(x=position.x, y=position.y + 1)) == "#")
        and (board.get(Position(x=position.x, y=position.y - 1)) == "#")
        and (board.get(Position(x=position.x, y=position.y)) == "#")
    )


def run_program(puzzle_input: List[int]) -> Program:
    program = initiate_program(puzzle_input, [])
    program, last_step = continue_program_till_no_input_or_halt(program, 0)
    return program


def solve_1(puzzle_input: List[int]) -> Dict[Position, str]:
    program = run_program(puzzle_input)
    board = transform_board(program.output)
    print_board(board)
    crossings = [
        position for position in list(board.keys()) if is_crossing(position, board)
    ]
    alignment_params = [position.x * position.y for position in crossings]
    return board, sum(alignment_params)


class Direction(IntEnum):
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3


class Turn(IntEnum):
    LEFT = -1
    RIGHT = 1


class Path(NamedTuple):
    turn: Turn
    length: int


class Robot(NamedTuple):
    position: Position
    direction: Direction


def get_new_direction(direction: Direction, turn: Turn) -> str:
    return (direction - turn) % 4


def move(position: Position, direction: Direction, length: int) -> Position:
    if direction == Direction.UP:
        return Position(x=position.x, y=position.y - length)
    if direction == Direction.LEFT:
        return Position(x=position.x - length, y=position.y)
    if direction == Direction.DOWN:
        return Position(x=position.x, y=position.y + length)
    if direction == Direction.RIGHT:
        return Position(x=position.x + length, y=position.y)


def get_paths(board: Dict[Position, str]) -> List[Path]:
    robot = Robot([key for key, val in board.items() if val == "^"][0], Direction.UP)
    done = False
    paths = []
    for k in range(50):
        for try_turn in Turn:
            new_direction = get_new_direction(robot.direction, try_turn)
            new_position = robot.position
            length = 0
            while board.get(new_position) in ["#", "^"]:
                length += 1
                new_position = move(robot.position, new_direction, length)
            if length <= 1:
                continue
            else:
                accepted_turn = try_turn
                accepted_length = length - 1

        new_path = Path(turn=accepted_turn, length=accepted_length)
        new_direction = get_new_direction(robot.direction, accepted_turn)
        new_position = move(robot.position, new_direction, accepted_length)
        robot = Robot(position=new_position, direction=new_direction)
        paths.append(new_path)
    return paths


def robot_run(puzzle_input: List[int], inputs: List[int]):
    program = initiate_program(puzzle_input, inputs)
    last_step = 0
    program, last_step = continue_program_till_no_input_or_halt(program, last_step)
    return program


def solve_2(puzzle_input: List[int], board: Dict[Position, str]):
    paths = get_paths(board)
    [print(f"Turn {int(path.turn)}, then walk {int(path.length)}") for path in paths]
    # manual labor to determine the sequences
    seq_a = [
        76,
        44,
        49,
        48,
        44,
        76,
        44,
        56,
        44,
        82,
        44,
        56,
        44,
        76,
        44,
        56,
        44,
        82,
        44,
        54,
        10,
    ]
    seq_b = [82, 44, 54, 44, 82, 44, 54, 44, 76, 44, 56, 44, 76, 44, 49, 48, 10]
    seq_c = [82, 44, 54, 44, 82, 44, 56, 44, 82, 44, 56, 10]
    order = [
        65,
        44,
        65,
        44,
        67,
        44,
        66,
        44,
        67,
        44,
        66,
        44,
        67,
        44,
        66,
        44,
        67,
        44,
        65,
        10,
    ]
    no = [110, 10]
    inputs = list(itertools.chain.from_iterable([order, seq_a, seq_b, seq_c, no]))

    program = robot_run(puzzle_input, inputs)
    return program.output[-1]


if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    puzzle_input = [int(x) for x in puzzle_input.split(",")]
    board, alignment = solve_1(puzzle_input)
    print("Result 1:", alignment)

    puzzle_input[0] = 2
    print("Result 2:", solve_2(puzzle_input, board))
