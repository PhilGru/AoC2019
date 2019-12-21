import enum
import itertools
import sys
from typing import List, NamedTuple, Set

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


def continue_program_till_no_input_or_halt(program: Program, last_step: int) -> Program:
    if last_step != 99:
        last_step = 0
    while (last_step != -1) and (last_step != 99):
        program, last_step = do_step(program)
    return program, last_step


####################################################################


class Position(NamedTuple):
    x: int
    y: int


def turn(curr_dir: int, turn_dir: int) -> int:
    curr_dir = curr_dir + (2 * turn_dir) - 1
    if curr_dir == -1:
        return 3
    if curr_dir == 4:
        return 0
    return curr_dir


def move(position: Position, direction: int) -> Position:
    if direction == 0:
        return Position(x=position.x, y=position.y - 1)
    if direction == 1:
        return Position(x=position.x + 1, y=position.y)
    if direction == 2:
        return Position(x=position.x, y=position.y + 1)
    if direction == 3:
        return Position(x=position.x - 1, y=position.y)
    raise ValueError(f"Wrong direction {direction}")


class Board:
    white: Set[Position]
    black: Set[Position]

    def __init__(self, white: Set[Position], black: Set[Position]):
        self.white = white
        self.black = black

    def get_board_value(self, position: Position) -> int:
        if position in self.white:
            return 1
        return 0

    def set_board_value(self, position: Position, value: int) -> None:
        if value == 0:
            self.black.add(position)
            if position in self.white:
                self.white.remove(position)
        elif value == 1:
            self.white.add(position)
            if position in self.black:
                self.black.remove(position)
        else:
            raise ValueError(f"Wrong board value {value}")


class Robot:
    program: Program
    direction: int  # 0: Up, 1: Right, 2: Down, 3: Left
    position: Position
    board: Board
    last_program_step: int

    def __init__(self, program, direction, position):
        self.program = program
        self.direction = direction
        self.position = position
        self.board = Board(white={Position(x=0, y=0)}, black=set())
        self.last_program_step = 0


def robot_step(robot: Robot) -> (Robot, bool):
    new_input = robot.board.get_board_value(robot.position)
    robot.program.inputs.append(new_input)
    robot.program, robot.last_program_step = continue_program_till_no_input_or_halt(
        robot.program, robot.last_program_step
    )
    robot.board.set_board_value(robot.position, robot.program.output[-2])
    robot.direction = turn(robot.direction, robot.program.output[-1])
    robot.position = move(robot.position, robot.direction)
    if robot.last_program_step == 99:
        return robot, True
    return robot, False


def initiate_robot(program: Program) -> Robot:
    return Robot(program=program, direction=0, position=Position(x=0, y=0))


def run_robot_till_halt(robot: Robot) -> Robot:
    done = False
    i = 0
    while not done:
        robot, done = robot_step(robot)
    return robot


def paint_board(puzzle_input: List[int]) -> Board:
    program = initiate_program(puzzle_input=puzzle_input, input_list=[])
    robot = initiate_robot(program=program)
    robot = run_robot_till_halt(robot)
    return robot.board


def print_board(board: Board) -> None:
    picture = []
    for i in range(-10, 10):
        row = []
        for j in range(-5, 50):
            if Position(x=j, y=i) in board.white:
                row.append("#")
            else:
                row.append(".")
        picture.append("".join(row))
    for col in picture:
        print(col)


def solve(puzzle_input: List[int]) -> int:
    board = paint_board(puzzle_input)
    print("Result 1:", len(board.white) + len(board.black))
    print("Result 2:")
    print_board(board)


if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    puzzle_input = [int(x) for x in puzzle_input.split(",")]
    solve(puzzle_input)
