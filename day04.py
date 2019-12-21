def check_number(nr: int) -> bool:
    stringed = str(nr)
    if sorted(stringed) != list(stringed):
        return False
    for digit in range(10):
        positions = [pos for pos in range(len(stringed)) if digit == int(stringed[pos])]
        if len(positions) == 2:
            if abs(positions[0] - positions[1]) == 1:
                return True
    return False


def check_numbers(lim_left: int, lim_right: int) -> int:
    counter = 0
    for i in range(lim_left, lim_right):
        if check_number(i):
            counter += 1
    return counter


if __name__ == "__main__":
    lim_left = 372037
    lim_right = 905157
    print("Result 2:", check_numbers(lim_left, lim_right))
