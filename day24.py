import sys
from enum import IntEnum
from typing import Dict, NamedTuple, NewType

class Position(NamedTuple):
    x: int
    y: int

class State(IntEnum):
    BUG = 0
    FREE = 1

Board = Dict[Position, int]

def parse_input(puzzle_input: str) -> Board:
    lines = puzzle_input.splitlines()
    board = {}
    for j, line in enumerate(lines):
        for i, pixel in enumerate(line):
            if pixel == "#":
                board[Position(x=i, y=j)] = State.BUG
            else:
                board[Position(x=i, y=j)] = State.FREE
    return board

def count_neighbors(board: Board, position: Position) -> int:
    counter = 0
    for x_shift in [-1, 1]:
        if board.get(Position(x=position.x+x_shift, y=position.y), State.FREE) == State.BUG:
            counter += 1
    for y_shift in [-1, 1]:
        if board.get(Position(x=position.x, y=position.y+y_shift), State.FREE) == State.BUG:
            counter += 1
    return counter

def print_board(board: Board):
    for j in range(5):
        row = ""
        for i in range(5):
            if board[Position(x=i, y=j)] == State.BUG:
                row += "#"
            if board[Position(x=i, y=j)] == State.FREE:
                row += "."
        print(row)


def step(board: Board) -> Board:
    new_board = {}
    for position, bug in board.items():
        nr_neighbors = count_neighbors(board, position)
        if ((nr_neighbors != 1) and (bug == State.BUG)):
            new_board[position] = State.FREE
        elif ((nr_neighbors in [1, 2]) and (bug == State.FREE)):
            new_board[position] = State.BUG
        else:
            new_board[position] = bug
    return new_board

def get_state(board: Board) -> int:
    state = 0
    for position, bug in board.items():
        if bug == State.BUG:
            state += pow(2, position.x + 5 * position.y)
    return state

def solve_1(puzzle_input: str):
    board = parse_input(puzzle_input)
    states = set()
    while True:
        state = get_state(board)
        print(state)
        if state in states:
            break
        states.add(state)
        board = step(board)

    print()
    print_board(board)

if __name__ == "__main__":
    puzzle_input = sys.stdin.read()
    solve_1(puzzle_input)
