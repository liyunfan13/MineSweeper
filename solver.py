from copy import deepcopy

from block_structure import blockStructure

# test
board = [
    [0, 0, 0, 0],
    [0, 1, 0, 1],
    [0, 1, 0, 1],
    [0, 0, 1, 0]
]
chain = []
safeList = []
explored = []
mines = []
totalMines = 5
size = 16
width = len(board[0])
height = len(board)

# param x: x-coordinate of the block
# param y: y-coordinate of the block
# explore next block
def nextStep(x, y):
    explored.append([x, y])
    curNum = getCurNum(x, y)
    if curNum != 'M' and len(explored) < size - totalMines:
        if len(chain) == 0:
            neigh = addNeighbor(x, y)
            addChain(x, y, neigh, int(curNum))
        else:
            neigh = addNeighbor(x, y)
            for points in neigh:
                if points in explored:
                    neigh.remove(points)
            updateChain(x, y, neigh, int(curNum))
        if len(safeList) > 0:
            for safePos in safeList:
                if safePos not in explored:
                    safeList.remove(safePos)
                    nextStep(safePos[0], safePos[1])
        else:
            for obj in chain:
                if obj.x == x and obj.y == y:
                    for i in [-1, 0, 1]:
                        for j in [-1, 0, 1]:
                            if checkValid(x, y, i, j) and [x + i, y + j] not in explored and [x + i, y + j] not in mines:
                                nextStep(x + i, y + j)
                    break
    elif curNum != 'M' and len(explored) == size - totalMines:
        print("Win!")
        exit()
    else:
        print("Lose!")
        exit()

def getCurNum(x, y):
    curNum = input("How many mines surround [" + str(x) + "," + str(y) + "] : ")
    return curNum

# param x: x-coordinate
# param y: y-coordinate
# param neigh: neighbors that are uncertain
# param curNum: mines to be found
# addChain: add a sub chain into the whole chain of influence
def addChain(x, y, neigh, curNum):
    if len(neigh) == curNum:
        for points in neigh:
            if points not in mines:
                mines.append(points)
    else:
        newObj = blockStructure(x, y, neigh, curNum)
        chain.append(newObj)

# param x: x-coordinate
# param y: y-coordinate
# param neigh: neighbors that are uncovered
# param curNum: mines to be found
# updateChain: update all the sub chains
def updateChain(x, y, neigh, curNum):
    tmp = deepcopy(neigh)
    for points in tmp:
        if points in safeList or points in explored:
            neigh.remove(points)
    newNum = curNum
    for points in tmp:
        if points in mines:
            neigh.remove(points)
            newNum -= 1
    if len(neigh) == newNum:
        for points in neigh:
            if points not in mines:
                mines.append(points)
                updateMine(points[0], points[1])
    if newNum == 0 and len(neigh) > 0:
        for points in neigh:
            if points not in safeList:
                safeList.append(points)
    length = len(chain)
    mine = newNum
    for obj in chain:
        if [x, y] in obj.neigh:
            obj.neigh.remove([x, y])
        repeat1 = 0
        repeat2 = 0
        tmp1 = []
        tmp2 = []

        for ele in obj.neigh:
            if ele in neigh:
                repeat1 += 1
                tmp1.append(ele)
        for ele in neigh:
            if ele in obj.neigh:
                repeat2 += 1
                tmp2.append(ele)
        if repeat1 == len(obj.neigh) and repeat1 < len(neigh) and repeat1 > 0:
            for ele in tmp1:
                neigh.remove(ele)
            mine = mine - obj.mine
        if repeat2 == len(neigh) and repeat2 < len(obj.neigh) and repeat2 > 0:
            for ele in tmp2:
                obj.neigh.remove(ele)
            obj.mine -= newNum

        if len(obj.neigh) == obj.mine:
            tmp3 = deepcopy(obj.neigh)
            for points in tmp3:
                if points not in mines:
                    mines.append(points)
                    obj.neigh.remove(points)
                    updateMine(points[0], points[1])
            obj.mine = 0
        elif obj.mine == 0 and len(obj.neigh) > 0:
            for coordinates in obj.neigh:
                if coordinates not in safeList:
                    safeList.append(coordinates)

        if mine == 0 and len(neigh) > 0:
            for coordinates in neigh:
                if coordinates not in safeList:
                    safeList.append(coordinates)
        length -= 1
        if length == 0:
            break
    if mine > 0 and len(neigh) > 0:
        addChain(x, y, neigh, mine)

# updateMine: once a mine is found, update the whole chain
def updateMine(x, y):
    for obj in chain:
        if [x, y] in obj.neigh:
            obj.neigh.remove([x, y])
            obj.mine -= 1
        if obj.mine == 0 and len(obj.neigh) > 0:
            for coordinates in obj.neigh:
                safeList.append(coordinates)

# addNeighbor: return current block's valid neighbor
def addNeighbor(x, y):
    neighbor = []
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if checkValid(x, y, i, j):
                neighbor.append([x + i, y + j])
    return neighbor

def checkValid(x, y, i, j):
    if (x + i == x) and (y + j == y):
        return False
    if (x + i < 0) or (y + j < 0):
        return False
    if (x + i > height - 1) or (y + j > width - 1):
        return False
    return True


#test

#neigh = addNeighbor(0,0)
#print(neigh)

# subChain = boxStructure(0,0,[[1,0],[1,1]],1,0)
# chain.append(subChain)
# print(subChain.neigh)
# subChain2 = [[0,2],[1,0],[1,1],[1,2]]
# updateChain(0,1,[[0,2],[1,0],[1,1],[1,2]],2)
# for a in chain:
#     print(a.neigh)
# print(safeList)

nextStep(0, 0)