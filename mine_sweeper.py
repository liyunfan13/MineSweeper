from mine_generate import mine_generate
import random


class Cell:
    def __init__(self, coordinate):
        self.clues = set()
        self.reveal = 0
        self.probability = 1.0
        self.coordinate = coordinate
        self.mined = -1


class MineSweeper(object):
    def __init__(self, width, length):
        self.width = width
        self.length = length

        self.unknown_cell = []
        for row in range(self.width):
            for col in range(self.length):
                self.unknown_cell.append([row, col])
        self.clear_cell = []
        self.mine_cell = []
        self.clue_cell = []  # info

        self.cells = []
        for row in range(self.width):
            self.cells.append([])
            for col in range(self.length):
                cell = Cell([row, col])
                self.cells[row].append(cell)
        self.cells[0][0].probability = 0.0

        self.chains = []

    def reveal_query(self, x, y):
        self.cells[x][y].reveal = int(input('The state of Position (' + str(x) + ', ' + str(y) + '): '))

    def clues_get(self, x, y):
        around = [[-1, -1], [0, -1], [1, -1],
                  [-1, 0], [1, 0],
                  [-1, 1], [0, 1], [1, 1]]
        clues = set()
        for i in range(len(around)):
            x_around = x + around[i][0]
            y_around = y + around[i][1]
            if x_around < 0 or y_around < 0 or x_around > self.width - 1 or y_around > self.length - 1 or \
                    self.cells[x_around][y_around].mined == 0:
                continue
            if self.cells[x_around][y_around].mined == 1:
                self.cells[x][y].reveal -= 1
            else:
                clues.add((x_around, y_around))

        if self.cells[x][y].mined == -1:
            self.unknown_cell.remove([x, y])
            self.clear_cell.append([x, y])
            self.cells[x][y].mined = 0
        self.cells[x][y].clues = clues
        self.renew_chains(x, y)

    def renew_chains(self, x, y):
        for chain in self.chains:
            if (x, y) in chain.clues:
                chain.clues.remove((x, y))
                chain.reveal -= self.cells[x][y].mined
            if len(chain.clues) == 0:
                self.chains.remove(chain)
                self.clue_cell.remove(chain.coordinate)

    def influence_chains(self, x, y):
        self.renew_chains(x, y)
        if len(self.cells[x][y].clues) == 0:
            return
        self.chains.append(self.cells[x][y])
        self.clue_cell.append([x, y])
        change = True
        while change:
            change = False
            for chain in self.chains:
                if chain.reveal != 0 and chain.reveal != len(chain.clues):
                    for chain_t in self.chains:
                        if chain_t != chain:
                            if chain_t.clues.issubset(chain.clues):
                                change = True
                                chain.clues -= chain_t.clues
                                chain.reveal -= chain_t.reveal
                else:
                    change = True
                    self.chains.remove(chain)
                    self.clue_cell.remove(chain.coordinate)
                    for clue in chain.clues:
                        self.cells[clue[0]][clue[1]].mined = chain.reveal / len(chain.clues)
                        self.cells[clue[0]][clue[1]].probability = self.cells[clue[0]][clue[1]].mined
                        if chain.reveal == 0:
                            self.clear_cell.append([clue[0], clue[1]])
                        else:
                            self.mine_cell.append([clue[0], clue[1]])
                        self.unknown_cell.remove([clue[0], clue[1]])
                        self.renew_chains(clue[0], clue[1])
        for chain in self.chains:
            probability = chain.reveal / len(chain.clues)
            for clue in chain.clues:
                self.cells[clue[0]][clue[1]].probability = probability

    def uncertainty(self, queue, front, rear):
        i = front
        while i < rear:
            if self.cells[queue[i][0]][queue[i][1]].probability > self.cells[queue[front][0]][queue[front][1]].probability:
                break
            i += 1
        r = random.randint(front, i - 1)
        t = queue[r]
        queue[r] = queue[front]
        queue[front] = t

    def info_display(self):
        print('Knowledge base about the board: ')
        print('Unknown cells: ', self.unknown_cell)
        print('Clear cells: ', self.clear_cell)
        print('Mine cells: ', self.mine_cell)
        print('Clue cells: ', self.clue_cell)

    def mine_sweeper(self):
        game_over = False
        next_step = [[-1, -1], [0, -1], [1, -1],
                     [-1, 0], [1, 0],
                     [-1, 1], [0, 1], [1, 1]]

        queue = [[0, 0]]
        visit = [[0 for col in range(self.length)] for row in range(self.width)]
        visit[0][0] = 1
        front = 0
        rear = 1  # search

        while front < rear:
            if len(self.unknown_cell) == 0:
                break
            if self.cells[queue[front][0]][queue[front][1]].probability != 0:
                self.uncertainty(queue, front, rear)
            x, y = queue[front][0], queue[front][1]
            front += 1
            if self.cells[x][y].mined != 1:
                self.info_display()
                self.reveal_query(x, y)
                if self.cells[x][y].reveal == -1:
                    game_over = True
                    break
                self.clues_get(x, y)
                self.influence_chains(x, y)

            for i in range(len(next_step)):
                x_next = x + next_step[i][0]
                y_next = y + next_step[i][1]
                if x_next < 0 or y_next < 0 or x_next > self.width - 1 or y_next > self.length - 1 or \
                        visit[x_next][y_next] == 1:
                    continue
                visit[x_next][y_next] = 1
                queue.append([x_next, y_next])
                rear += 1
                
            for i in range(front + 1, rear):  # sort queue according to probability
                key = queue[i]
                j = i - 1
                while j >= front and self.cells[queue[j][0]][queue[j][1]].probability > \
                        self.cells[key[0]][key[1]].probability:
                    queue[j + 1] = queue[j]
                    j -= 1
                queue[j + 1] = key

            # for i in range(front, rear):
                # print('probability', queue[i], self.cells[queue[i][0]][queue[i][1]].probability)

        if game_over:
            print('Game over, computer lost!')
        else:
            self.info_display()
            print('Computer win!')

    def test(self):
        self.mine_sweeper()
        for row in range(self.width):
            for col in range(self.length):
                print((row, col), self.cells[row][col].clues)
        print(type(self.cells[0][0].coordinate))


if __name__ == '__main__':
    width = 4
    length = 5
    num = 5
    board = mine_generate(width, length, num)
    print(board)

    mine_sweeper = MineSweeper(width, length)
    mine_sweeper.mine_sweeper()
