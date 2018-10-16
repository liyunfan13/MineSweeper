import numpy
import random


def mine_generate(width, length, nums):
    board = numpy.zeros((width + 2, length + 2), int)
    board[0, :] = 1
    board[width + 1, :] = 1
    board[:, 0] = 1
    board[:, length + 1] = 1
    temp = numpy.array(board)
    check = True
    count = 0
    max_count = 10000
    while check and count < max_count:  # 10000 in case that there is no successful grid
        check = False
        n = 0
        temp = numpy.array(board)
        while n < nums:  # add mines
            row = random.randint(1, width)
            col = random.randint(1, length)
            if (row == 1 and col == 1) or temp[row, col] == 1:
                continue
            temp[row, col] = 1
            n += 1

        for row in range(1, width + 1):  # check reasonableness
            for col in range(1, length + 1):
                if temp[row - 1, col - 1] == 1 and temp[row - 1, col] == 1 and temp[row - 1, col + 1] == 1 and \
                        temp[row, col - 1] == 1 and temp[row, col] == 1 and temp[row, col + 1] == 1 and \
                        temp[row + 1, col - 1] == 1 and temp[row + 1, col] == 1 and temp[row + 1, col + 1] == 1:
                    check = True
                    break
            if check:
                break
        count += 1
    return temp[1:width + 1, 1:length + 1]


# test
a = mine_generate(3, 4, 9)
print(a)
