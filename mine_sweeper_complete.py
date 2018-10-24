from mine_generate import mine_generate


class Cell:
    def __init__(self, coordinate):
        self.clues = set()
        self.reveal = 0
        self.probability = 1.0
        self.neighbor = 0
        self.coordinate = coordinate
        self.mined = -1


class MineSweeper(object):
    def __init__(self, width, length, num):
        self.width = width
        self.length = length
        self.num = num

        self.coordinate = (0, 0)
        self.game_over = False

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

    def reveal_query(self):
        self.cells[self.coordinate[0]][self.coordinate[1]].reveal = int(
            input('The state of Position (' + str(self.coordinate[0]) + ', ' + str(self.coordinate[1]) + '): '))

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

    def queue_sort(self, queue, front, rear):
        for i in range(front + 1, rear):  # sort queue according to probability, insertion sort for almost sorted array
            key = queue[i]
            j = i - 1
            while j >= front and self.cells[queue[j][0]][queue[j][1]].probability > \
                    self.cells[key[0]][key[1]].probability:
                queue[j + 1] = queue[j]
                j -= 1
            queue[j + 1] = key
        # for i in range(front, rear):
        # print('probability', queue[i], self.cells[queue[i][0]][queue[i][1]].probability)

    def get_neighbor(self):
        around = [[-1, -1], [0, -1], [1, -1],
                  [-1, 0], [1, 0],
                  [-1, 1], [0, 1], [1, 1]]
        for row in range(self.width):
            for col in range(self.length):
                count = 0
                for i in range(len(around)):
                    x_around = row + around[i][0]
                    y_around = col + around[i][1]
                    if x_around < 0 or y_around < 0 or x_around > self.width - 1 or y_around > self.length - 1 or \
                            self.cells[x_around][y_around].mined != -1:
                        continue
                    count += 1
                self.cells[row][col].neighbor = count

    def uncertainty(self, queue, visit, front, rear):
        q_prob = self.cells[queue[front][0]][queue[front][1]].probability
        c_prob = (self.num - len(self.mine_cell)) / len(self.unknown_cell)
        self.get_neighbor()
        if q_prob > c_prob:
            neighbor = 9
            for row in range(self.width):
                for col in range(self.length):
                    if visit[self.cells[row][col].coordinate[0]][self.cells[row][col].coordinate[1]] == 1 or \
                            self.cells[row][col].probability != 1:
                        continue
                    if self.cells[row][col].neighbor < neighbor:
                        neighbor = self.cells[row][col].neighbor
                        coor = self.cells[row][col].coordinate
            self.cells[coor[0]][coor[1]].probability = c_prob
            visit[coor[0]][coor[1]] = 1
            queue.append([coor[0], coor[1]])
            rear += 1
            self.queue_sort(queue, front, rear)
        else:
            i = front
            while i < rear:
                if self.cells[queue[i][0]][queue[i][1]].probability > q_prob:
                    break
                i += 1
            pos = front
            for j in range(front + 1, i):
                if self.cells[queue[j][0]][queue[j][1]].neighbor < self.cells[queue[pos][0]][queue[pos][1]].neighbor:
                    pos = j
            t = queue[pos]
            queue[pos] = queue[front]
            queue[front] = t

    def info_display(self):
        print('Knowledge base about the board: ')
        print('Unknown cells: ', self.unknown_cell)
        print('Clear cells: ', self.clear_cell)
        print('Mine cells: ', self.mine_cell)
        print('Clue cells: ', self.clue_cell)

    def mine_sweeper(self):
        next_step = [[-1, -1], [0, -1], [1, -1],
                     [-1, 0], [1, 0],
                     [-1, 1], [0, 1], [1, 1]]

        queue = [[0, 0]]
        visit = [[0 for col in range(self.length)] for row in range(self.width)]
        visit[0][0] = 1
        front = 0
        rear = 1  # search

        while front < rear:
            if len(self.unknown_cell) == 0 or len(self.mine_cell) == self.num:
                break
            if self.cells[queue[front][0]][queue[front][1]].probability != 0:
                self.uncertainty(queue, visit, front, rear)
            x, y = queue[front][0], queue[front][1]
            front += 1
            if self.cells[x][y].mined != 1:
                self.info_display()
                self.coordinate = (x, y)
                self.reveal_query()
                if self.cells[x][y].reveal == -1:
                    self.game_over = True
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

            self.queue_sort(queue, front, rear)


if __name__ == '__main__':
    width = 3
    length = 4
    num = 3
    board = mine_generate(width, length, num)
    print(board)

    mine_sweeper = MineSweeper(width, length, num)
    mine_sweeper.mine_sweeper()

    if mine_sweeper.game_over:
        print('Game over, computer lost!')
    else:
        mine_sweeper.info_display()
        print('Computer win!')
