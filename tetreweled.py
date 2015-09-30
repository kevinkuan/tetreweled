# Tetreweled
# Kevin Kuan

from Tkinter import *
import math
import random
import copy
import time


def timerFired(canvas):
    if (canvas.data.menuScreen == True):
        redrawAll(canvas)
    elif (canvas.data.menuScreen == False and canvas.data.gameOver == False):
        redrawAll(canvas)
        if (int(time.time() - canvas.data.gameTime) > canvas.data.countDown):
            if (canvas.data.swappingBlocks == False and canvas.data.swappingBlockAI == False):
                if (canvas.data.VSComScreen == True):
                    doRoutineAI(canvas)
                doRoutinePlayer(canvas)
            else:
                if (canvas.data.swappingBlocks == True and canvas.data.swappingBlockAI == False):
                    transitionSwap(canvas)
                    if (canvas.data.VSComScreen == True):
                        doRoutineAI(canvas)
                if (canvas.data.swappingBlocks == False and canvas.data.swappingBlockAI == True):
                    transitionSwapAI(canvas)
                    doRoutinePlayer(canvas)
                if (canvas.data.swappingBlocks == True and canvas.data.swappingBlockAI == True):
                    transitionSwapAI(canvas)
                    transitionSwap(canvas)
    else:
        redrawAll(canvas)
    delay = 75# milliseconds
    def f():
        timerFired(canvas) # DK: define local fn in closure
    canvas.after(delay, f) # pause, then call timerFired again


def doRoutineAI(canvas):
    #checkForCursors(canvas)
    makeAIMove(canvas)
    updateGrounded(canvas, True)
    doGravity(canvas, True)
    checkForClear(canvas, True)
    doFlag(canvas, True)
    checkForStreak(canvas, True)
    checkForAlive(canvas, True)
    resetStreak(canvas, False)
    checkForRiseUp(canvas, True)
    sendGarbage(canvas, True)

def doRoutinePlayer(canvas):
    updateGrounded(canvas, False)
    doGravity(canvas, False)
    checkForClear(canvas, False)
    doFlag(canvas, False)
    checkForStreak(canvas, False)
    checkForAlive(canvas, False)
    resetStreak(canvas, False)
    checkForRiseUp(canvas, False)
    checkTimeAttack(canvas)
    checkGarbage(canvas, False)
    sendGarbage(canvas, False)

def sendGarbage(canvas, forAI):
    if (canvas.data.VSComScreen == True):
        if (forAI == True):
            score = canvas.data.AIScore
        else:
            score = canvas.data.score
        if (score > canvas.data.scoreToGarbage):
            makeGarbage(canvas, not forAI)
            score -= canvas.data.scoreToGarbage
        if (forAI == True):
            canvas.data.AIScore = score
        else:
            canvas.data.score = score

def checkGarbage(canvas, forAI):
    #print time.time() - canvas.data.gameTime
    if (canvas.data.garbageScreen == True):
        if (time.time() - canvas.data.gameTime > canvas.data.garbageTime
            and checkForNoAction(canvas, forAI) == True):
            canvas.data.garbageTime = time.time() - canvas.data.gameTime + 8 - ((canvas.data.difficulty - 1) * 2)
            makeGarbage(canvas, forAI)

def makeGarbage(canvas, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    rows = canvas.data.rows
    cols = canvas.data.cols
    (derpRow, highestCol) = findBiggestCols(canvas, forAI)
    highestRow = findColumnHeight(canvas, forAI, highestCol)
    for col in xrange(cols):
        if (highestRow == rows - 1 and board[highestRow][col].alive == True):
            canvas.data.gameOver = True
            canvas.data.AILost = forAI
    b = Block(rows - 1, 0, canvas.data.garbage)
    b.alive = True
    b.isGarbage = True
    b.isGrounded = False
    board[rows-1][0] = b
    if (forAI == True):
        canvas.data.AIBoard = board
    else:
        canvas.data.board = board

def findColumnHeight(canvas, forAI, col):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    rows = canvas.data.rows
    length = 0
    for row in xrange(rows):
        if (board[row][col].alive == False):
            return row
    return row

def checkForCursors(canvas):
    board = canvas.data.AIBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    counter = 0
    for row in xrange(rows):
        for col in xrange(cols):
            if (board[row][col].isSelected == True):
                counter += 1
    if (counter > 1):
        for row in xrange(rows):
            for col in xrange(cols):
                if (board[row][col].isSelected == True):
                    board[row][col].isSelected = False
    canvas.data.AIBoard = board

def makeAIMove(canvas):
    if (len(canvas.data.currentPowerupAI) == 1):
        checkWhatPowerup(canvas, True)
    if (int(time.time() - canvas.data.gameTime) % canvas.data.timeBetweenMove == 0):
        (garbagePresent, garbageRow, garbageCol) = isGarbagePresent(canvas)
        if (canvas.data.swappingBlockAI == False and checkForNoAction(canvas, True) == True
            and currentFlashingBlocks(canvas, True) == False and canvas.data.movingToDestination == False):
            canvas.data.madeMoveAI = True
            board = canvas.data.AIBoard
            possibleMoves = findPossibleMoves(canvas)
            #print "possible moves",possibleMoves
            possibleMovesDirection = findPossibleMovesDirection(canvas, possibleMoves)
            cleanedList = cleanList(canvas, possibleMovesDirection)
            if (checkForNoAction(canvas, True) == True and len(cleanedList) > 0):
                executeListMove(canvas, cleanedList)
            else:
                executeSomething(canvas)
        elif (canvas.data.movingToDestination == True):
            doSwapAI(canvas)
        else:
            rows = canvas.data.rows
            (highestRow, highestCol) = findBiggestCols(canvas, True)
            if (highestRow < rows / 2):
                riseUp(canvas, True)
            else:
                shortenHeight(canvas)

def executeSomething(canvas):
    difficulty = canvas.data.difficulty
    if (difficulty == 1):
        chance = random.randint(0, 20)
    elif (difficulty == 2):
        chance = random.randint(0,50)
    else:
        chance = random.randint(0,100)
    if (chance > 10):
        shortenHeight(canvas)
    else:
        board = canvas.data.AIBoard
        rows = canvas.data.rows
        cols = canvas.data.cols
        row = random.randint(0,rows - 1)
        col = random.randint(0, cols - 2)
        while (board[row][col].alive == False):
            row = random.randint(0,rows - 1)
            col = random.randint(0, cols - 2)
        canvas.data.destination = (row,col)
        canvas.data.movingToDestination = True

def shortenHeight(canvas):
    board = canvas.data.AIBoard
    cols = canvas.data.cols
    """
    for col in xrange(cols):
        if (board[row-1][col].alive == True and board[row-1][col].isGrounded == True):
            print "found this", row-1, col
            (currentRow, currentCol) = row-1,col
            break
    else:
    """
    (currentRow, currentCol) = findBiggestCols(canvas, True)
    (targetRow, targetCol) = findNearestHole(canvas)
    #print "highest at ", currentRow, currentCol, "go to", targetRow, targetCol
    if (currentRow == targetRow):
        pass
    elif (targetCol != currentCol):
        if (targetCol > currentCol):
            canvas.data.destination = (currentRow, currentCol)
        else:
            canvas.data.destination = (currentRow, currentCol - 1)
    canvas.data.movingToDestination = True

def findNearestHole(canvas):
    board = canvas.data.AIBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    (isGarbage, garbageRow, garbageCol) = isGarbagePresent(canvas)
    for row in xrange(garbageRow):
        for col in xrange(cols-1, -1, -1):
            if(board[row][col].alive == False):
                return (row, col)
    (currentRow, currentCol) = findBiggestCols(canvas, True)
    return (0, 5 - currentCol)

def isGarbagePresent(canvas):
    board = canvas.data.AIBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    for row in xrange(rows):
        for col in xrange(cols):
            if(board[row][col].isGarbage == True):
                return True, row, col
    return False, 0, 0

def cleanList(canvas, possibleMovesDirection):
    freshList = []
    board = canvas.data.AIBoard
    cols = canvas.data.cols
    for index in xrange(len(possibleMovesDirection)):
        (row,col) = (possibleMovesDirection[index][0], possibleMovesDirection[index][1])
        if (possibleMovesDirection[index][1] > 0 and
            possibleMovesDirection[index][1] < cols - 1 and
            possibleMovesDirection[index][2] != -10 and
            board[row][col].alive == True):
            freshList.append(possibleMovesDirection[index])
    return freshList

def executeListMove(canvas, possibleMoves):
    board = canvas.data.AIBoard
    randomMove = random.randint(0, len(possibleMoves) - 1)
    row = possibleMoves[randomMove][0]
    col = possibleMoves[randomMove][1]
    #board[row][col].isSelected = True
    #printColors(canvas)
    canvas.data.destination = (row,col)
    canvas.data.movingToDestination = True

def doSwapAI(canvas):
    board = canvas.data.AIBoard
    (currentRow, currentCol) = findSelectedBlockAI(canvas)
    (newRow, newCol) = canvas.data.destination
    #print currentRow, newRow
    if (currentRow < newRow):
        moveToDestination(canvas, +1, 0)
    elif (currentRow > newRow):
        moveToDestination(canvas, -1, 0)
    elif (currentCol < newCol):
        moveToDestination(canvas, 0, +1)
    elif (currentCol > newCol):
        moveToDestination(canvas, 0, -1)
    elif (board[newRow][newCol].isGarbage == True):
        canvas.data.movingToDestination = False
    elif (currentRow == newRow and currentCol == newCol):
        canvas.data.movingToDestination = False
        board = canvas.data.AIBoard
        if (board[newRow][newCol].isFlashing == board[newRow][newCol+1].isFlashing == False):
            canvas.data.swappingBlockAI = True
            transitionSwapAI(canvas)

def moveToDestination(canvas, drow, dcol):
    board = canvas.data.AIBoard
    (currentRow, currentCol) = findSelectedBlockAI(canvas)
    newRow = currentRow + drow
    newCol = currentCol + dcol
    board[currentRow][currentCol].isSelected = False
    board[newRow][newCol].isSelected = True
    canvas.data.AIBoard = board 

def transitionSwapAI(canvas):
    board = canvas.data.AIBoard
    (currentRow, currentCol) = findSelectedBlockAI(canvas)
    block1 = board[currentRow][currentCol]
    block2 = board[currentRow][currentCol+1]
    if (canvas.data.swappingBlockAI == True and almostEquals(currentCol + 1,block1.y) == False):
        #print "still swapping"
        block1.y = block1.y + .5
        block2.y = block2.y - .5
    else:
        #print "done swapping"
        block1.swapBlocks(block2)
        block1.y = block1.y - 1
        block2.y = block2.y + 1
        canvas.data.swappingBlockAI = False
    board[currentRow][currentCol] = block1
    board[currentRow][currentCol+1] = block2
    canvas.data.AIBoard = board

def findSelectedBlockAI(canvas):
    board = canvas.data.AIBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    for row in xrange(rows):
        for col in xrange(cols):
            block = board[row][col]
            if (block.isSelected == True):
                return (row,col)
    return (2,2)
    
    
def findPossibleMovesDirection(canvas, possibleMoves):
    dirs = [(0,1),] # left, right, down, up
    possibleMovesDirection = []
    board = canvas.data.AIBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    value = 0
    for index in xrange(len(possibleMoves)):
        directionToSwap = (0,1)
        (currentRow, currentCol, targetColor) = possibleMoves[index]
        for dir in dirs:
            counter = 1
            (drow, dcol) = dir
            newRow = currentRow + drow
            newCol = currentCol + dcol
            if (newRow >= 0 and newRow < rows-1 and newCol >= 0 and newCol < cols - 1):
                if (currentRow + 2 < rows - 1 and board[currentRow+1][currentCol].color == board[currentRow+2][currentCol].color == targetColor):
                    directionToSwap = (0,1)
                    counter += 2
                    value = counter
                    break
                elif (newRow + 2 < rows - 1 and board[newRow+1][newCol].color == board[newRow+2][newCol].color == targetColor):
                    directionToSwap = (drow, dcol)
                    counter += 2
                    value = counter
                    break
                elif (newCol + 2 < cols - 1 and board[newRow][newCol+1].color == board[newRow][newCol+2].color == targetColor):
                    directionToSwap = (0, 1)
                    counter += 2
                    value = counter
                    break
                elif (newCol - 2 > 0 and board[newRow][newCol-1].color == board[newRow][newCol-2].color == targetColor):
                    directionToSwap = (0, 1)
                    counter += 2
                    value = counter
                    break
                elif (board[currentRow-1][currentCol].color == board[currentRow+1][currentCol].color == targetColor):
                    directionToSwap = (0, 1)
                    extendedRow = 0
                    while (currentRow-1-extendedRow > 0 and board[currentRow-1-extendedRow][currentCol].color == targetColor):
                        counter += 1
                        extendedRow += 1
                    extendedRow = 0
                    while (currentRow+1+extendedRow < rows - 1 and board[currentRow+1+extendedRow][newCol].color == targetColor):
                        counter += 1
                        extendedRow += 1
                    value = counter
                    break
                elif (board[newRow-1][newCol].color == board[newRow+1][newCol].color == targetColor):
                    directionToSwap = (drow, dcol)
                    extendedRow = 0
                    while (newRow-1-extendedRow > 0 and board[newRow-1-extendedRow][newCol].color == targetColor):
                        counter += 1
                        extendedRow += 1
                    extendedRow = 0
                    while (newRow+1+extendedRow < rows - 1 and board[newRow+1+extendedRow][newCol].color == targetColor):
                        counter += 1
                        extendedRow += 1
                    value = counter
                    break
                elif (board[currentRow][currentCol+1].color == board[currentRow][currentCol-1].color == targetColor):
                    directionToSwap = (0, 1)
                    extendedCol = 0
                    while (currentCol-1-extendedCol > 1 and board[currentRow][currentCol-1-extendedCol].color == targetColor):
                        counter += 1
                        extendedCol += 1
                    extendedCol = 0
                    while (currentCol+1+extendedCol < cols - 1 and board[currentRow][currentCol+1+extendedCol].color == targetColor):
                        counter += 1
                        extendedCol += 1
                    value = counter
                    break
                elif (board[newRow][newCol+1].color == board[newRow][newCol-1].color == targetColor):
                    directionToSwap = (drow, dcol)
                    extendedCol = 0
                    while (newCol-1-extendedCol > 1 and board[newRow][newCol-1-extendedCol].color == targetColor):
                        counter += 1
                        extendedCol += 1
                    extendedCol = 0
                    while (newCol+1+extendedCol < cols - 1 and board[newRow][newCol+1+extendedCol].color == targetColor):
                        counter += 1
                        extendedCol += 1
                    value = counter
                    break
                elif (currentRow - 2 >= 0 and board[currentRow-1][currentCol].color == board[currentRow-2][currentCol].color == targetColor):
                    directionToSwap = (0, 1)
                    counter += 2
                    value = counter
                    break
                elif (newRow - 2 >= 0 and board[newRow-1][newCol].color == board[newRow-2][newCol].color == targetColor):
                    directionToSwap = (drow, dcol)
                    counter += 2
                    value = counter
                    break
        (dirRow, dirCol) = directionToSwap
        possibleMovesDirection.append([currentRow, currentCol, dirRow, dirCol, value])
    return possibleMovesDirection

def findPossibleMoves(canvas):
    #copyBoard(canvas)
    possibleMoves = []
    rows = canvas.data.rows
    cols = canvas.data.cols
    if (checkForNoAction(canvas, True)) == True:
        for row in xrange(rows):
            for col in xrange(cols):
                if (col != cols - 1):
                    possibleMoves = checkPossibleHorizontal(canvas, possibleMoves, row, col)
                elif (row != rows - 1):
                    possibleMoves = checkPossibleVertical(canvas, possibleMoves, row, col)
    #print canvas.data.AIBoard == canvas.data.currentState
    return possibleMoves

def checkPossibleHorizontal(canvas, possibleMoves, row, col):
    switchBlockValues(canvas, row, col, row, col+1, True)
    moveColor = checkForClearAI(canvas)
    if (moveColor != 0):
        possibleMoves.append((row,col,moveColor))
    switchBlockValues(canvas, row, col, row, col+1, True)
    unflag(canvas)
    return possibleMoves

def checkPossibleVertical(canvas, possibleMoves, row, col):
    switchBlockValues(canvas, row, col, row+1, col, True)
    moveColor = checkForClearAI(canvas)
    if (moveColor != 0):
        possibleMoves.append((row,col,moveColor))
    switchBlockValues(canvas, row, col, row+1, col, True)
    unflag(canvas)
    return possibleMoves

def unflag(canvas):
    board = canvas.data.AIBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    for row in xrange(rows):
        for col in xrange(cols):
            board[row][col].flag = False
    canvas.data.AIBoard = board

def copyBoard(canvas):
    board = canvas.data.AIBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    currentState = canvas.data.currentState
    for row in xrange(rows):
        for col in xrange(cols):
            currentState[row][col].copyBlock(board[row][col])
    canvas.data.currentState = currentState

def checkForClearAI(canvas):
    doHorizontalStuffAI(canvas)
    resetValuesAI(canvas)
    doVerticalStuffAI(canvas)
    resetValuesAI(canvas)
    moveColor = countMoveColor(canvas)
    return moveColor

def countMoveColor(canvas):
    board = canvas.data.AIBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    color = 0
    for row in xrange(rows):
        for col in xrange(cols):
            if (board[row][col].flag == True):
                color = board[row][col].color
    return color
    
def doHorizontalStuffAI(canvas):
    board = canvas.data.AIBoard
    clearBoard = canvas.data.clearBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    for row in xrange(rows):
        for col in xrange(cols):
            checkHorizontalClearAI(canvas,row,col,clearBoard)
    for row in xrange(rows):
        for col in xrange(cols):
            if (clearBoard[row][col] >= 2):
                board[row][col-1].flag = True
                board[row][col].flag = True
                board[row][col+1].flag = True
    canvas.data.AIBoard = board

def doVerticalStuffAI(canvas):
    board = canvas.data.AIBoard
    clearBoard = canvas.data.clearBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    for row in xrange(rows):
        for col in xrange(cols):
            checkVerticalClearAI(canvas,row,col,clearBoard)
    for row in xrange(rows):
        for col in xrange(cols):
            if (clearBoard[row][col] >= 2):
                board[row-1][col].flag = True
                board[row][col].flag = True
                board[row+1][col].flag = True
    canvas.data.AIBoard = board


def resetValuesAI(canvas):
    rows = canvas.data.rows
    cols = canvas.data.cols
    clearBoard = canvas.data.clearBoard
    resetBoard = canvas.data.resetBoard
    for row in xrange(rows):
        for col in xrange(cols):
            clearBoard[row][col] = 0
    canvas.data.clearBoard = clearBoard

def checkHorizontalClearAI(canvas,row,col,clearBoard):
    board = canvas.data.AIBoard
    cols = canvas.data.cols
    middleColor = board[row][col].color
    middleAlive = board[row][col].alive
    middleGrounded = board[row][col].isGrounded
    if (col == cols-1):
        pass
    else:
        rightColor = board[row][col+1].color
        rightAlive = board[row][col+1].alive
        rightGrounded = board[row][col+1].isGrounded
        if (middleColor == rightColor and (middleAlive == rightAlive == True)
            and (middleGrounded == rightGrounded == True)):
            clearBoard[row][col] += 1
            clearBoard[row][col+1] += 1
    canvas.data.clearBoard = clearBoard

def checkVerticalClearAI(canvas,row,col, clearBoard):
    board =  canvas.data.AIBoard
    rows = canvas.data.rows
    middleColor = board[row][col].color
    middleAlive = board[row][col].alive
    middleGrounded = board[row][col].isGrounded
    if (row == rows-1):
        pass
    else:
        upColor = board[row+1][col].color
        upAlive = board[row+1][col].alive
        upGrounded = board[row+1][col].isGrounded
        if (middleColor == upColor and (middleAlive == upAlive == True)
            and (middleGrounded == upGrounded == True) and (board[row][col].isFlashing == board[row+1][col].isFlashing == False)):
            clearBoard[row][col] += 1
            clearBoard[row+1][col] += 1
    canvas.data.clearBoard = clearBoard

def checkHorizontalClear(canvas,row,col,clearBoard, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    cols = canvas.data.cols
    middleColor = board[row][col].color
    middleAlive = board[row][col].alive
    middleGrounded = board[row][col].isGrounded
    if (col == cols-1):
        pass
    else:
        rightColor = board[row][col+1].color
        rightAlive = board[row][col+1].alive
        rightGrounded = board[row][col+1].isGrounded
        if (middleColor == rightColor and (middleAlive == rightAlive == True)
            and (middleGrounded == rightGrounded == True)):
            clearBoard[row][col] += 1
            clearBoard[row][col+1] += 1
    if (forAI == True):
        canvas.data.AIBoard = board
    else:
        canvas.data.board = board

def checkVerticalClear(canvas,row,col, clearBoard, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    rows = canvas.data.rows
    middleColor = board[row][col].color
    middleAlive = board[row][col].alive
    middleGrounded = board[row][col].isGrounded
    if (row == rows-1):
        pass
    else:
        upColor = board[row+1][col].color
        upAlive = board[row+1][col].alive
        upGrounded = board[row+1][col].isGrounded
        if (middleColor == upColor and (middleAlive == upAlive == True)
            and (middleGrounded == upGrounded == True) and (board[row][col].isFlashing == board[row+1][col].isFlashing == False)):
            clearBoard[row][col] += 1
            clearBoard[row+1][col] += 1
    if (forAI == True):
        canvas.data.AIBoard = board
    else:
        canvas.data.board = board


def resetStreak(canvas, forAI):
    rows = canvas.data.rows
    cols = canvas.data.cols
    streakBoard = canvas.data.streakBoard
    resetBoard = canvas.data.resetBoard
    if (checkForNoAction(canvas, forAI) == True):
        for row in xrange(rows):
            for col in xrange(cols):
                streakBoard[row][col] = 0
    canvas.data.streakBoard = streakBoard

def checkForNoAction(canvas, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    rows = canvas.data.rows
    cols = canvas.data.cols
    for row in xrange(rows):
        for col in xrange(cols):
            if (board[row][col].isFlashing == True or
                (board[row][col].alive == True and board[row][col].isGrounded == False)):
                return False
    return True

def printColors(canvas):
    board = canvas.data.board
    streakBoard = canvas.data.streakBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    counter = 0
    for row in xrange(rows):
        for col in xrange(cols):
            if(board[row][col].isGarbage == True):
                return (int((time.time() - board[row][col].timeStartFlashing) * 10), board[row][col].alive, board[row][col].flag)
            
            
        
def checkTimeAttack(canvas):
    if (canvas.data.timeAttackScreen == True):
        currentTime = int(time.time() - canvas.data.gameTime)
        if (currentTime > canvas.data.maxTimeAttack + canvas.data.countDown):
            canvas.data.gameOver = True

def checkForRiseUp(canvas, forAI):
    if (forAI == True):
        startTime = canvas.data.startTimeAI
        timeToRise = canvas.data.timeToRiseAI
    else:
        startTime = canvas.data.startTime
        timeToRise = canvas.data.timeToRise
        
    if (currentFlashingBlocks(canvas, forAI) == True or allGrounded(canvas, forAI) == False):
        if (forAI == True):
            canvas.data.startTimeAI += (time.time() - canvas.data.differenceAI)
        else:
            canvas.data.startTime += (time.time() - canvas.data.difference)
    elif (time.time() - startTime - canvas.data.countDown > timeToRise):
        if (currentFlashingBlocks(canvas, forAI) == False and allGrounded(canvas, forAI) == True):
            riseUp(canvas, forAI)
            if (forAI == False):
                if (canvas.data.timeToRise > canvas.data.maxTime):
                    canvas.data.timeToRise -= 0.2
                canvas.data.startTime = time.time()
            else:
                if (canvas.data.timeToRiseAI > canvas.data.maxTime):
                    canvas.data.timeToRiseAI -= 0.2
                canvas.data.startTimeAI = time.time()
    if (forAI == False):
        canvas.data.difference = time.time()
    else:
        canvas.data.differenceAI = time.time()
        
    

def allGrounded(canvas, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    rows = canvas.data.rows
    cols = canvas.data.cols
    for row in xrange(rows):
        for col in xrange(cols):
            if (board[row][col].isGrounded == True):
                return True
    return False

def currentFlashingBlocks(canvas, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    rows = canvas.data.rows
    cols = canvas.data.cols
    for row in xrange(rows):
        for col in xrange(cols):
            if (board[row][col].isFlashing == True):
                return True
    return False

def checkForStreak(canvas, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    streakBoard = canvas.data.streakBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    for row in xrange(rows):
        for col in xrange(cols):
            if (board[row][col].flag == True):
                tempRow = row
                tempCol = col
                while (tempRow < rows - 1):
                    streakBoard[tempRow+1][tempCol] = streakBoard[row][col]
                    tempRow += 1
    canvas.data.streakBoard = streakBoard

def findHighestStreak(canvas):
    streakBoard = canvas.data.streakBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    biggest = 0
    for row in xrange(rows):
        for col in xrange(cols):
            if (streakBoard[row][col] > 0):
                biggest = streakBoard[row][col]
    return biggest

def checkForAlive(canvas, forAI):
    rows = canvas.data.rows
    cols = canvas.data.cols
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    for row in xrange(rows):
        for col in xrange(cols):
            if (board[row][col].alive == False or board[row][col].color == ""):
                board[row][col].color = ""
                board[row][col].alive = False
                board[row][col].isFlashing = False
                board[row][col].timeStartFlashing = 0
                tempRow = row
                tempCol = col
                while (tempRow < rows - 1):
                    board[tempRow][col].isGrounded = False
                    tempRow += 1
    if (forAI == True):
        canvas.data.AIBoard = board
    else:
        canvas.data.board = board

def doGravity(canvas, forAI):
    updateGrounded(canvas, forAI)
    isRowFlashing = False
    rows = canvas.data.rows
    cols = canvas.data.cols
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    for row in xrange(rows):
        for col in xrange(cols):
            if (board[row][0].isGarbage == True and col != 0):
                pass
            else:
                if (board[row][col].alive == True and board[row][col].isGrounded == False
                    and board[row][col].isFlashing == False):
                    lowestRow = findLowestFlash(canvas, forAI, row, col)
                    #if (lowestRow != row - 1):
                    switchBlockValues(canvas, row, col, row-1, col, forAI)
                    if (forAI == True):
                        board = canvas.data.AIBoard
                    else:
                        board = canvas.data.board
                    isRowFlashing = False
    if (forAI == True):
        canvas.data.AIBoard = board
    else:
        canvas.data.board = board

def findLowestFlash(canvas, forAI, currentRow, currentCol):
    rows = canvas.data.rows
    cols = canvas.data.cols
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    for tempRow in xrange(currentRow, -1, -1):
        if (board[tempRow][currentCol].isFlashing == True):
            return tempRow
    return -1


def updateGrounded(canvas, forAI):
    rows = canvas.data.rows
    cols = canvas.data.cols
    blockUnder = False
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    for row in xrange(rows):
        for col in xrange(cols):
                if (board[row][0].isGarbage == True):
                    for tempCol in xrange(cols):
                        if (board[row-1][tempCol].alive == True and board[row-1][tempCol].isGrounded == True):
                            #print "something under", row -1, tempCol, board[row-1][tempCol].alive, board[row-1][tempCol].color, board[row-1][tempCol].isGrounded
                            blockUnder = True
                    if (blockUnder == True): 
                        board[row][0].isGrounded = True
                    else:
                        board[row][0].isGrounded = False
                else:
                    if (board[row][col].isFlashing == False):
                        if (row == 0):
                            board[row][col].isGrounded = True
                        elif (row > 0 and board[row-1][col].alive == False):
                            board[row][col].isGrounded = False
                        elif (board[row-1][col].isGrounded == False):
                            board[row][col].isGrounded = False
                        elif (board[row][col].color == ""):
                            board[row][col].isGrounded = False
                        else:
                            board[row][col].isGrounded = True
                    elif (board[row][col].isFlashing == True):
                        if (row != row - 1):
                            board[row+1][col].isGrounded = True
                blockUnder = False
    if (forAI == True):
        canvas.data.AIBoard = board
    else:
        canvas.data.board = board
    


def createBoard2Players(canvas):
    rows = canvas.data.rows
    cols = canvas.data.cols
    board = [ ]
    board2 = [ ]
    board3 = [ ]
    board4 = [ ]
    board5 = [ ]
    for row in range(rows):
        board += [[0] * cols]
        board2 += [[0] * cols]
        board3 += [[0] * cols]
        board4 += [[0] * cols]
        board5 += [[0] * cols]
    canvas.data.board = board
    canvas.data.clearBoard = board2
    canvas.data.resetBoard = board3
    canvas.data.streakBoard = board4
    canvas.data.AIBoard =  board5
    canvas.data.currentState = copy.deepcopy(canvas.data.resetBoard)
    loadBoardAI(canvas)
    loadBoard(canvas)

def createBoard(canvas):
    rows = canvas.data.rows
    cols = canvas.data.cols
    board = [ ]
    board2 = [ ]
    board3 = [ ]
    board4 = [ ]
    for row in range(rows):
        board += [[0] * cols]
        board2 += [[0] * cols]
        board3 += [[0] * cols]
        board4 += [[0] * cols]
    canvas.data.board = board
    canvas.data.clearBoard = board2
    canvas.data.resetBoard = board3
    canvas.data.streakBoard = board4
    loadBoard(canvas)

def loadBoard(canvas):
    board = canvas.data.board
    rows = canvas.data.rows
    cols = canvas.data.cols
    colors = canvas.data.colorImages
    for row in xrange(rows):
        for col in xrange(cols):
            if (row < rows/2):
                colorIndex = random.randint(0,len(colors)-2)
                b = Block(row, col, colors[colorIndex])
            else:
                b = Block(row, col, "")
                b.alive = False
                b.isGrounded = False
            board[row][col] = b
    board[0][2].isSelected = True
    canvas.data.board = board
    for i in xrange(10):
        noColorsTogether(canvas, False)

def loadBoardAI(canvas):
    board = canvas.data.AIBoard
    currentState = canvas.data.currentState
    rows = canvas.data.rows
    cols = canvas.data.cols
    colors = canvas.data.colorImages
    for row in xrange(rows):
        for col in xrange(cols):
            if (row < rows/2):
                colorIndex = random.randint(0,len(colors)-2)
                b = Block(row, col, colors[colorIndex])
                c = Block(row, col, colors[colorIndex])
            else:
                b = Block(row, col, "black")
                b.alive = False
                c = Block(row, col, "black")
                c.alive = False
                b.isGrounded = False
                c.isGrounded = False
            board[row][col] = b
            currentState[row][col] = c
    canvas.data.AIBoard = board
    canvas.data.currentState = currentState
    for i in xrange(10):
        noColorsTogether(canvas, True)

def noColorsTogether(canvas, forAI):
    if (forAI == True):
        doHorizontalInitialCheck(canvas, True)
        resetValues(canvas)
        doVerticalInitialCheck(canvas, True)
        resetValues(canvas)
    else:
        doHorizontalInitialCheck(canvas, False)
        resetValues(canvas)
        doVerticalInitialCheck(canvas, False)
        resetValues(canvas)

def doHorizontalInitialCheck(canvas, forAI):
    if (canvas.data.VSComScreen == True and forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    clearBoard = canvas.data.clearBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    colors = canvas.data.colorImages
    colorIndex = random.randint(0,len(colors)-2)
    for row in xrange(rows):
        for col in xrange(cols):
            block = board[row][col]
            if (forAI == True):
                checkHorizontalClear(canvas,row,col,clearBoard, True)
            else:
                checkHorizontalClear(canvas,row,col,clearBoard, False)
    for row in xrange(rows):
        for col in xrange(cols):
            if (clearBoard[row][col] >= 2):
                while (board[row][col].color == colors[colorIndex]):
                    colorIndex = random.randint(0,len(colors)-2)
                board[row][col].color = colors[colorIndex]
    if (canvas.data.VSComScreen == True and forAI == True):
        canvas.data.AIBoard = board
    else:
        canvas.data.board = board

def doVerticalInitialCheck(canvas, forAI):
    if (canvas.data.VSComScreen == True and forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    clearBoard = canvas.data.clearBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    colors = canvas.data.colorImages
    colorIndex = random.randint(0,len(colors)-2)
    for row in xrange(rows):
        for col in xrange(cols):
            block = board[row][col]
            if (forAI == True):
                checkVerticalClear(canvas,row,col,clearBoard, True)
            else:
                checkVerticalClear(canvas,row,col,clearBoard, False)
    for row in xrange(rows):
        for col in xrange(cols):
            if (clearBoard[row][col] >= 2):
                while (board[row][col].color == colors[colorIndex]):
                    colorIndex = random.randint(0,len(colors)-2)
                board[row][col].color = colors[colorIndex]
    if (canvas.data.VSComScreen == True and forAI == True):
        canvas.data.AIBoard = board
    else:
        canvas.data.board = board

def mousePressed(canvas, event):
    redrawAll(canvas)
    width = canvas.data.width
    height = canvas.data.height
    if (canvas.data.instructionsScreen == True or canvas.data.settingsScreen == True):
        print "Back"
        canvas.data.menuScreen = True
        canvas.data.onePlayerScreen = False
        canvas.data.marathonScreen = False
        canvas.data.timeAttackScreen = False
        canvas.data.VSComScreen = False
        canvas.data.garbageScreen = False
        canvas.data.instructionsScreen = False
        canvas.data.settingsScreen = False
    if (canvas.data.menuScreen == True and event.x > width/3 and event.x < 2*width/3
        and event.y < height * 5.5 / 10 and event.y > height * 4.5 / 10):
        if (canvas.data.onePlayerScreen == False):
            canvas.data.onePlayerScreen = True
            print "one player"
        elif (canvas.data.onePlayerScreen == True and canvas.data.VSComScreen == True):
            print "easy mode"
            canvas.data.difficulty = 1
            canvas.data.menuScreen = False
            initVSCom(canvas)
        elif (canvas.data.onePlayerScreen == True and (canvas.data.timeAttackScreen == True)):
            print "easy mode"
            canvas.data.difficulty = 1
            canvas.data.menuScreen = False
            initTimeAttack(canvas)
        elif (canvas.data.onePlayerScreen == True and canvas.data.marathonScreen == True):
            print "easy mode"
            canvas.data.difficulty = 1
            canvas.data.menuScreen = False
            initMarathon(canvas)
        elif (canvas.data.onePlayerScreen == True and canvas.data.garbageScreen == True):
            print "easy mode"
            canvas.data.difficulty = 1
            canvas.data.menuScreen = False
            initGarbage(canvas)
        elif (canvas.data.onePlayerScreen == True and canvas.data.marathonScreen == False):
            canvas.data.marathonScreen = True
            print "marathon"
    elif (canvas.data.menuScreen == True and event.x > width/3 and event.x < 2*width/3
        and event.y < height * 7 / 10 and event.y > height * 6 / 10):
        if (canvas.data.onePlayerScreen == False):
            canvas.data.VSComScreen = True
            canvas.data.onePlayerScreen = True
            print "VS com"
        elif (canvas.data.onePlayerScreen == True and (canvas.data.marathonScreen == True)):
            print "medium mode"
            canvas.data.difficulty = 2
            canvas.data.menuScreen = False
            initMarathon(canvas)
        elif (canvas.data.onePlayerScreen == True and (canvas.data.timeAttackScreen == True)):
            print "medium mode"
            canvas.data.difficulty = 2
            canvas.data.menuScreen = False
            initTimeAttack(canvas)
        elif (canvas.data.onePlayerScreen == True and canvas.data.VSComScreen == True):
            print "medium mode"
            canvas.data.difficulty = 2
            canvas.data.menuScreen = False
            initVSCom(canvas)
        elif (canvas.data.onePlayerScreen == True and canvas.data.garbageScreen == True):
            print "medium mode"
            canvas.data.difficulty = 2
            canvas.data.menuScreen = False
            initGarbage(canvas)
        elif (canvas.data.onePlayerScreen == True and canvas.data.timeAttackScreen == False):
            canvas.data.timeAttackScreen = True
            print "time attack"
    elif (canvas.data.menuScreen == True and event.x > width/3 and event.x < 2*width/3
        and event.y < height * 8 / 10 and event.y > height * 7 / 10):
        if (canvas.data.onePlayerScreen == False):
            canvas.data.settingsScreen = True
            print "Settings"
        elif (canvas.data.onePlayerScreen == True and (canvas.data.marathonScreen == True)):
            print "hard mode"
            canvas.data.difficulty = 3
            canvas.data.menuScreen = False
            initMarathon(canvas)
        elif (canvas.data.onePlayerScreen == True and (canvas.data.timeAttackScreen == True)):
            print "hard mode"
            canvas.data.difficulty = 3
            canvas.data.menuScreen = False
            initTimeAttack(canvas)
        elif (canvas.data.onePlayerScreen == True and canvas.data.VSComScreen == True):
            print "hard mode"
            canvas.data.difficulty = 3
            canvas.data.menuScreen = False
            initVSCom(canvas)
        elif (canvas.data.onePlayerScreen == True and canvas.data.garbageScreen == True):
            print "hard mode"
            canvas.data.difficulty = 3
            canvas.data.menuScreen = False
            initGarbage(canvas)
        elif (canvas.data.onePlayerScreen == True and canvas.data.garbageScreen == False):
            canvas.data.garbageScreen = True
            print "Garbage"
    elif (canvas.data.menuScreen == True and event.x > width/3 and event.x < 2*width/3
        and event.y < height * 9 / 10 and event.y > height * 8 / 10):
        if (canvas.data.onePlayerScreen == False):
            canvas.data.instructionsScreen = True
            print "Instructions"
        elif (canvas.data.onePlayerScreen == True):
            print "Back"
            canvas.data.menuScreen = True
            canvas.data.onePlayerScreen = False
            canvas.data.marathonScreen = False
            canvas.data.timeAttackScreen = False
            canvas.data.VSComScreen = False
            canvas.data.garbageScreen = False
            canvas.data.settingsScreen = False
            canvas.data.instructionsScreen = False
            canvas.data.settingsScreen = False
            
    
 
def keyPressed(canvas, event):
    if (canvas.data.menuScreen == False):
        if (canvas.data.gameOver == False and canvas.data.swappingBlocks != True):
            (currentRow, currentCol) = findSelectedBlock(canvas)
            rows = canvas.data.rows
            cols = canvas.data.cols
            if (event.keysym == "Up" and currentRow < rows - 1):
                """
                clearRow = PhotoImage(file = 'clear_row.gif')
                temp = canvas.data.currentPowerup
                temp.append(clearRow)
                canvas.data.currentPowerup = temp
                """
                moveCursor(canvas, 1,0)
            elif (event.keysym == "Down" and currentRow > 0):
                moveCursor(canvas,-1,0)
            elif (event.keysym == "Left" and currentCol > 0):
                moveCursor(canvas,0,-1)
            elif (event.keysym == "Right" and currentCol < cols - 2):
                moveCursor(canvas,0,1)
            elif (event.keysym == "space"):
                riseUp(canvas, False)
            elif (event.keysym == "1"):
                checkWhatPowerup(canvas, False)
            if (int(time.time() - canvas.data.gameTime) > canvas.data.countDown):
                if (event.char == "x"):
                    doSwap(canvas)
            redrawAll(canvas)
        elif (event.char == "r"):
            init(canvas)


def checkWhatPowerup(canvas, forAI):
    if (forAI == True):
        currentPowerup = canvas.data.currentPowerupAI
    else:
        currentPowerup = canvas.data.currentPowerup
    powerUps = canvas.data.powerUps
    if (len(currentPowerup) != 0):
        for powerUp in powerUps:
            if (currentPowerup[0] == powerUp):
                # "clear row", "clear col", "homogenize", "freeze time"
                if (currentPowerup[0] == powerUps[0]):
                    doClearRow(canvas, forAI)
                elif (currentPowerup[0] == powerUps[1]):
                    doClearCol(canvas, forAI)
                elif (currentPowerup[0] == "homogenize"):
                    doClearCol(canvas)
                elif (currentPowerup[0] == powerUps[2]):
                    doFreezeTime(canvas, forAI)
        currentPowerup.pop(0)

def doFreezeTime(canvas, forAI):
    canvas.data.freezeTime = True
    canvas.data.freezeTimeElapsed = time.time()
    if (forAI == True):
        startTime = canvas.data.startTimeAI
    else:
        startTime = canvas.data.startTime
    startTime += 6
    if (forAI == True):
        canvas.data.startTimeAI = startTime
    else:
        canvas.data.startTime = startTime
    

def transitionSwap(canvas):
    board = canvas.data.board
    (currentRow, currentCol) = findSelectedBlock(canvas)
    block1 = board[currentRow][currentCol]
    block2 = board[currentRow][currentCol+1]
    if (canvas.data.swappingBlocks == True and almostEquals(currentCol + 1,block1.y) == False):
        block1.y = block1.y + .5
        block2.y = block2.y - .5
    else:
        block1.swapBlocks(block2)
        block1.y = block1.y - 1
        block2.y = block2.y + 1
        canvas.data.swappingBlocks = False
    board[currentRow][currentCol] = block1
    board[currentRow][currentCol+1] = block2
    canvas.data.board = board

def almostEquals(d1, d2):
    epsilon = 0.000001
    return (abs(d2 - d1) < epsilon)

def doSwap(canvas):
    board = canvas.data.board
    (currentRow, currentCol) = findSelectedBlock(canvas)
    if (board[currentRow][currentCol].isFlashing == board[currentRow][currentCol+1].isFlashing == False
        and board[currentRow][currentCol].isGarbage == False):
        canvas.data.swappingBlocks = True
        transitionSwap(canvas)



def switchBlockValues(canvas, row, col, row2, col2, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    rows = canvas.data.rows
    block1 = board[row][col]
    block2 = board[row2][col2]
    block1.swapBlocks(block2)
    board[row][col] = block1
    board[row2][col2] = block2
    if (forAI == True):
        canvas.data.AIBoard = board
    else:
        canvas.data.board = board

def findSelectedBlock(canvas):
    board = canvas.data.board
    rows = canvas.data.rows
    cols = canvas.data.cols
    for row in xrange(rows):
        for col in xrange(cols):
            block = board[row][col]
            if (block.isSelected == True):
                return (row,col)
    return (2,2)

def riseUp(canvas, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    rows = canvas.data.rows
    cols = canvas.data.cols
    for row in xrange(rows-1,-1, -1):
        for col in xrange(cols):
            if (row == rows-1 and board[row][col].alive == True):
                canvas.data.gameOver = True
                canvas.data.AILost = forAI
                canvas.data.endTime = time.time()
            if (row == 0 and canvas.data.gameOver == False):
                board[row][col] = createRandomBlock(canvas, row, col, forAI)
            else:
                if (canvas.data.gameOver == False):
                    canvas.data.risingUp = True
                    switchBlockValues(canvas, row, col, row-1, col, forAI)
                    canvas.data.risingUp = False
    if (canvas.data.gameOver == False):
        if (forAI == True):
            (currentRow, currentCol) = findSelectedBlockAI(canvas)
        else:
            (currentRow, currentCol) = findSelectedBlock(canvas)
        if (currentRow != rows - 1):
            board[currentRow][currentCol].isSelected = False
            board[currentRow+1][currentCol].isSelected = True
    if (forAI == True):
        canvas.data.AIBoard = board
        canvas.data.AIScore = canvas.data.AIScore + (10 * canvas.data.difficulty)
    else:
        canvas.data.board = board
        canvas.data.score = canvas.data.score + (10 * canvas.data.difficulty)
    



def doClearRow(canvas, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    rows = canvas.data.rows
    cols = canvas.data.cols
    for row in xrange(0,2,1):
        for col in xrange(cols):
            if (board[row][col].alive == True):
                board[row][col].flag = True
    if (forAI == True):
        canvas.data.AIBoard = board
    else:
        canvas.data.board = board
    
def doClearCol(canvas, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    rows = canvas.data.rows
    cols = canvas.data.cols
    (biggestRow, biggestCol) = findBiggestCols(canvas, forAI)
    for row in xrange(rows):
        if (board[row][biggestCol].alive == True):
            board[row][biggestCol].flag = True
    if (forAI == True):
        canvas.data.AIBoard = board
    else:
        canvas.data.board = board


def findBiggestCols(canvas, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    rows = canvas.data.rows
    cols = canvas.data.cols
    bigCols = []
    biggestColNumber = 0
    biggestRowNumber = 0
    biggest = 0
    for col in xrange(cols):
        row = 0
        length = 0
        while (board[row][col].alive == True and board[row][col].isGarbage == False):
            length += 1
            row += 1
        row -= 1
        if (length > biggest):
            biggestColNumber = col
            biggestRowNumber = row
            biggest = length
        elif (length == biggest):
            if (random.randint(0,1) == 0):
                biggestColNumber = col
                biggestRowNumber = row
                biggest = length
    return (biggestRowNumber,biggestColNumber)

def createRandomBlock(canvas, row, col, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    colors = canvas.data.colorImages
    colorIndex = random.randint(0,len(colors)-1)
    if (col > 1):
        while (colors[colorIndex] == board[row][col-1].color and board[row][col-2].color):
            colorIndex = random.randint(0,len(colors)-1)
    b = Block(row, col, colors[colorIndex])
    return b

def moveCursor(canvas,drow,dcol):
    board = canvas.data.board
    (currentRow, currentCol) = findSelectedBlock(canvas)
    newRow = currentRow + drow
    newCol = currentCol + dcol
    board[currentRow][currentCol].isSelected = False
    board[newRow][newCol].isSelected = True
    canvas.data.board = board

def checkForClear(canvas, forAI):
    if (forAI == True):
        doHorizontalStuff(canvas, True)
        resetValues(canvas)
        doVerticalStuff(canvas, True)
        resetValues(canvas)
    doHorizontalStuff(canvas, False)
    resetValues(canvas)
    doVerticalStuff(canvas, False)
    resetValues(canvas)
    
def doHorizontalStuff(canvas, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    clearBoard = canvas.data.clearBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    for row in xrange(rows):
        for col in xrange(cols):
            if (forAI == True):
                checkHorizontalClear(canvas,row,col,clearBoard, True)
            else:
                checkHorizontalClear(canvas,row,col,clearBoard, False)
    for row in xrange(rows):
        for col in xrange(cols):
            if (clearBoard[row][col] >= 2):
                board[row][col-1].flag = True
                board[row][col].flag = True
                board[row][col+1].flag = True
    if (forAI == True):
        canvas.data.AIBoard = board
    else:
        canvas.data.board = board

def doVerticalStuff(canvas, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    clearBoard = canvas.data.clearBoard
    rows = canvas.data.rows
    cols = canvas.data.cols
    for row in xrange(rows):
        for col in xrange(cols):
            if (forAI == True):
                checkVerticalClear(canvas,row,col,clearBoard, True)
            else:
                checkVerticalClear(canvas,row,col,clearBoard, False)
    for row in xrange(rows):
        for col in xrange(cols):
            if (clearBoard[row][col] >= 2 and board[row][col].color != canvas.data.garbage):
                board[row-1][col].flag = True
                board[row][col].flag = True
                board[row+1][col].flag = True
    if (forAI == True):
        canvas.data.AIBoard = board
    else:
        canvas.data.board = board


def resetValues(canvas):
    rows = canvas.data.rows
    cols = canvas.data.cols
    clearBoard = canvas.data.clearBoard
    resetBoard = canvas.data.resetBoard
    for row in xrange(rows):
        for col in xrange(cols):
            clearBoard[row][col] = resetBoard[row][col]
    canvas.data.clearBoard = clearBoard

def doFlag(canvas, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
        score = canvas.data.AIScore
    else:
        board = canvas.data.board
        score = canvas.data.score
    rows = canvas.data.rows
    cols = canvas.data.cols
    streakBoard = canvas.data.streakBoard
    power = canvas.data.powerColor
    highestStreak = findHighestStreak(canvas)
    for row in xrange(rows):
        for col in xrange(cols):
            if (board[row][col].flag == True and board[row][col].isFlashing == False):
                board[row][col].isFlashing = True
                board[row][col].timeStartFlashing = time.time()
                streakBoard[row][col] = highestStreak + 1
                if (board[row][col].color != power):
                    score += 100 * canvas.data.difficulty * streakBoard[row][col]
                if (board[row][col].color == power and canvas.data.hasSelectedPowerup == False):
                    randomizePowerup(canvas, forAI)
                if (row < rows - 1 and board[row+1][0].color == canvas.data.garbage):
                    board[row+1][0].isFlashing = True
                    board[row+1][0].flag = True
                    for col in xrange(cols):
                        board[row+1][col] = createRandomBlock(canvas, row+1, col, doFlag)
                        board[row+1][col].alive = True
                        board[row+1][col].timeStartFlashing = time.time()
                    board[row+1][0].isGarbage = True   
            #print board[row][0].timeStartFlashing 
            if (board[row][col].isGarbage == True and board[row][col].timeStartFlashing != 0 and (int((time.time() - board[row][col].timeStartFlashing) * 10) >= canvas.data.maxFlashTime)):
                for tempCol in xrange(cols):
                    board[row][tempCol].alive = True
                board[row][0].isGarbage = False
                board[row][0].flag = False
            elif (board[row][col].flag == True and (int((time.time() - board[row][col].timeStartFlashing) * 10) >= canvas.data.maxFlashTime)):
                board[row][col].alive = False
                board[row][col].flag = False
    if (forAI == True):
        canvas.data.AIBoard = board
        canvas.data.AIScore = score
    else:
        canvas.data.board = board
        canvas.data.score = score
    canvas.data.streakBoard = streakBoard
    canvas.data.hasSelectedPowerup = False

def resetGarbage(canvas, forAI):
    if (forAI == True):
        board = canvas.data.AIBoard
    else:
        board = canvas.data.board
    rows = canvas.data.rows
    cols = canvas.data.cols
    for row in xrange(rows):
        for col in xrange(cols):
            board[row][col].isGarbage = False
    if (forAI == True):
        canvas.data.AIBoard = board
    else:
        canvas.data.board = board

def randomizePowerup(canvas, forAI):
    if (forAI == True):
        currentPowerup = canvas.data.currentPowerupAI
    else:
        currentPowerup = canvas.data.currentPowerup
    if (len(currentPowerup) < 1):
        powerUps = canvas.data.powerUps
        randomIndex = random.randint(0,len(powerUps)-1)
        selectedPowerup = powerUps[randomIndex]
        if (forAI == True):
            canvas.data.currentPowerupAI.append(selectedPowerup)
        else:
            canvas.data.currentPowerup.append(selectedPowerup)
        canvas.data.hasSelectedPowerup = True

def redrawAll(canvas): # DK: redrawAll() --> redrawAll(canvas)
    canvas.delete(ALL)
    if (canvas.data.menuScreen == True):
        drawMenu(canvas)
    else:
        if (canvas.data.VSComScreen == False):
            drawGame(canvas)
        else:
            drawAIGame(canvas)
        if (canvas.data.gameOver == True):
            drawGameOver(canvas)

def drawGame(canvas):
    rows = canvas.data.rows
    cols = canvas.data.cols
    board = canvas.data.board
    drawBackground(canvas)
    for row in xrange(rows):
        for col in xrange(cols):
            if (board[row][col].alive == True or board[row][0].isGarbage == True):
                drawBlock(canvas, row, col)
    drawCursor(canvas)
    drawBorder(canvas)
    if (int(time.time() - canvas.data.gameTime < canvas.data.countDown)):
        drawCountDown(canvas)

def drawCountDown(canvas):
    height = canvas.data.height
    width = canvas.data.width
    if (int(time.time() - canvas.data.gameTime) < 1):
        canvas.create_text(width / 2, height / 2, text="3", font=("Helvetica", 200), fill = "gray")
    elif (int(time.time() - canvas.data.gameTime) >= 1 and int(time.time() - canvas.data.gameTime) < 2):
        canvas.create_text(width / 2, height / 2, text="2", font=("Helvetica", 200), fill = "gray")
    elif (int(time.time() - canvas.data.gameTime) >= 2 and int(time.time() - canvas.data.gameTime) < 3):
        canvas.create_text(width / 2, height / 2, text="1", font=("Helvetica", 200), fill = "gray")
    else:
        canvas.create_text(width / 2, height / 2, text="Go!", font=("Helvetica", 200), fill = "gray")

def drawBorder(canvas):
    height = canvas.data.height
    canvas.create_rectangle(200,50,560,height - 50, width = 1, outline = "white")
    
def drawBorderAI(canvas):
    height = canvas.data.height
    width = canvas.data.width
    canvas.create_rectangle(20,50,380,height - 50, width = 1, outline = "white")
    canvas.create_rectangle(20, height - 40, 20 + 360* (canvas.data.score * 1.0 / canvas.data.scoreToGarbage),height - 40, outline = "red", fill = "red")

    canvas.create_rectangle(width - 380,50,width - 20,height - 50, width = 1, outline = "white")
    canvas.create_rectangle(width - 380, height - 40, width - 380 + 360 * (canvas.data.AIScore * 1.0 / canvas.data.scoreToGarbage),height - 40, outline = "red", fill = "red")

def drawAIGame(canvas):
    rows = canvas.data.rows
    cols = canvas.data.cols
    board = canvas.data.board
    AIboard = canvas.data.AIBoard
    drawBackground2Player(canvas)
    for row in xrange(rows):
        for col in xrange(cols):
            if (board[row][col].alive == True):
                drawBlock2Player(canvas, row, col)
            if (AIboard[row][col].alive == True):
                drawBlockAI(canvas, row, col)
    drawCursor2Player(canvas)
    drawAICursor(canvas)
    drawBorderAI(canvas)
    if (int(time.time() - canvas.data.gameTime < canvas.data.countDown)):
        drawCountDown(canvas)

def drawBackground(canvas):
    width = canvas.data.width
    height = canvas.data.height
    score = canvas.data.score
    powerUps = canvas.data.currentPowerup
    if (canvas.data.freezeTime == True and time.time() - canvas.data.freezeTimeElapsed < 6):
        canvas.create_rectangle(0,0,width, height, fill = "light blue")
    else:
        canvas.create_rectangle(0,0,width, height, fill = "black")
    canvas.create_text(width * 3 / 4, 100, text="Score:", font=("Helvetica", 50), fill = "white")
    canvas.create_text(width * 3 / 4, 150, text=str(score), font=("Helvetica", 50), fill = "white")
    drawTime(canvas)
    canvas.create_text(width * 3 / 4, 500, text="Power Up:", font=("Helvetica", 50), fill = "white")
    if (len(powerUps) != 0):
        for i in xrange(len(powerUps)):
            canvas.create_image((width * 3 / 4) - 50, 550 + (i * 50), image = powerUps[i], anchor = NW)
    canvas.create_rectangle((width * 3 / 4) - 50, 550, (width * 3 / 4) + 50, 650, width = 2, outline = "white")
    #canvas.create_text(width * 3 / 4, 550 + (i * 50), text=canvas.data.currentPowerup[i], font=("Helvetica", 50), fill = "white")

def drawBackground2Player(canvas):
    width = canvas.data.width
    height = canvas.data.height
    score = canvas.data.score
    powerUps = canvas.data.currentPowerup
    powerUpsAI = canvas.data.currentPowerupAI
    if (canvas.data.freezeTime == True and time.time() - canvas.data.freezeTimeElapsed < 6):
        canvas.create_rectangle(0,0,width/3, height, fill = "light blue")
    else:
        canvas.create_rectangle(0,0,width, height, fill = "black")
    if (canvas.data.gameOver == False):
        drawTime2Player(canvas)
    canvas.create_text(width / 2, 100, text="Power Up:", font=("Helvetica", 50), fill = "white")
    canvas.create_text(width / 2, 550, text="Power Up:", font=("Helvetica", 50), fill = "white")
    if (len(powerUps) != 0):
        for i in xrange(len(powerUps)):
            canvas.create_image((width / 2) - 50, 150 + (i * 50), image = powerUps[i], anchor = NW)
    elif (len(powerUpsAI) != 0):
        for i in xrange(len(powerUps)):
            canvas.create_image((width / 2) - 50, 550 + (i * 50), image = powerUpsAI[i], anchor = NW)     
    canvas.create_rectangle((width / 2) - 50, 650, (width / 2) + 50, 750, width = 2, outline = "white")
    canvas.create_rectangle((width / 2) - 50, 150, (width / 2) + 50, 250, width = 2, outline = "white")
    
def drawTime(canvas):
    width = canvas.data.width
    minutes = (int(time.time() - canvas.data.gameTime) - canvas.data.countDown) / 60
    canvas.create_text(width * 3 / 4, 300, text="Time:", font=("Helvetica", 50), fill = "white")
    if (int(time.time() - canvas.data.gameTime) > canvas.data.countDown):
        if (canvas.data.timeAttackScreen == False and canvas.data.gameOver == False):
            if ((int(time.time() - canvas.data.gameTime) - canvas.data.countDown) % 60 < 10):
                canvas.create_text(width * 3 / 4, 350, text=str(minutes) + ":0" +  str(int(time.time() - canvas.data.gameTime - canvas.data.countDown) % 60),
                                   font=("Helvetica", 50), fill = "white")
            else:
                canvas.create_text(width * 3 / 4, 350, text=str(minutes) + ":" +  str(int(time.time() - canvas.data.gameTime - canvas.data.countDown) % 60),
                                   font=("Helvetica", 50), fill = "white")
        elif (canvas.data.timeAttackScreen == True and canvas.data.gameOver == False):
            currentTime = canvas.data.maxTimeAttack - int(time.time() - canvas.data.gameTime) + canvas.data.countDown
            minutes = currentTime / 60
            if (currentTime % 60 < 10):
                canvas.create_text(width * 3 / 4, 350, text=str(minutes) + ":0" +  str(currentTime % 60),
                                   font=("Helvetica", 50), fill = "white")
            else:
                canvas.create_text(width * 3 / 4, 350, text=str(minutes) + ":" +  str(currentTime% 60),
                                   font=("Helvetica", 50), fill = "white")
        elif (canvas.data.timeAttackScreen == False and canvas.data.gameOver == True):
            if (int(canvas.data.endTime - canvas.data.gameTime) % 60 < 10):
                canvas.create_text(width * 3 / 4, 350, text=str(minutes) + ":0" +  str(int(canvas.data.endTime - canvas.data.gameTime) % 60),
                                   font=("Helvetica", 50), fill = "white")
            else:
                canvas.create_text(width * 3 / 4, 350, text=str(minutes) + ":" +  str(int(canvas.data.endTime- canvas.data.gameTime) % 60),
                                   font=("Helvetica", 50), fill = "white")
        else:
            canvas.create_text(width * 2, 350, text = str(time.time() - canvas.data.endTime), font=("Helvetica", 50), fill = "white")
    else:
        if (canvas.data.timeAttackScreen == True):
            canvas.create_text(width * 3 / 4, 350, text="2:00", font=("Helvetica", 50), fill = "white")
        else:
            canvas.create_text(width * 3 / 4, 350, text="0:00", font=("Helvetica", 50), fill = "white")

def drawTime2Player(canvas):
    width = canvas.data.width
    height = canvas.data.height
    minutes = int(time.time() - canvas.data.gameTime - canvas.data.countDown) / 60
    canvas.create_text(width / 2, height / 2 - 50, text="Time:", font=("Helvetica", 50), fill = "white")
    if (int(time.time() - canvas.data.gameTime) > canvas.data.countDown):
        if (canvas.data.gameOver == False):
            if (int(time.time() - canvas.data.gameTime - canvas.data.countDown) % 60 < 10):
                canvas.create_text(width / 2, height / 2, text=str(minutes) + ":0" +  str(int(time.time() - canvas.data.gameTime - canvas.data.countDown) % 60),
                                   font=("Helvetica", 50), fill = "white")
            else:
                canvas.create_text(width / 2, height / 2, text=str(minutes) + ":" +  str(int(time.time() - canvas.data.gameTime - canvas.data.countDown) % 60),
                                   font=("Helvetica", 50), fill = "white")
    else:
        canvas.create_text(width /2 , height / 2, text="0:00", font=("Helvetica", 50), fill = "white")

def drawBlock(canvas, row, col):
    board = canvas.data.board
    (currentRow, currentCol) = findSelectedBlock(canvas)
    block = board[row][col]
    x = board[row][col].x
    y = board[row][col].y
    canvasHeight = canvas.data.height
    blockSize = canvas.data.blockSize
    maxFlashTime = canvas.data.maxFlashTime
    color = block.color
    streakBoard = canvas.data.streakBoard
    if (color != canvas.data.garbage and block.isFlashing == True):
        if ((int((time.time() - block.timeStartFlashing) * 10) % 2) == 0):
            color = canvas.data.whiteColor
        else:
            color = block.color
    elif (board[row][0].isGarbage == True):
        if ((int((time.time() - block.timeStartFlashing) * 10) % 2) == 0):
            if (col == 0):
                color = canvas.data.garbage
            else:
                color = ""
        else:
            color = block.color
    canvas.create_image(200 + y* blockSize, canvasHeight - 50 - (x+1)*blockSize, image = color, anchor = NW)
    #canvas.create_text(220 + y * blockSize + 30, canvasHeight - (x+1)*blockSize - 30,  text=str(streakBoard[row][col]), font=("Helvetica", 30))
    #canvas.create_rectangle(col * blockSize, canvasHeight - (row+1)*blockSize, (col+1) * blockSize, canvasHeight - (row * blockSize), fill = color)
    #canvas.create_text(col * blockSize + 20, canvasHeight - (row+1)*blockSize + 20, text=str(clearBoard[row][col]), font=("Helvetica", 16))
    
def drawBlock2Player(canvas, row, col):
    board = canvas.data.board
    (currentRow, currentCol) = findSelectedBlock(canvas)
    block = board[row][col]
    x = board[row][col].x
    y = board[row][col].y
    canvasHeight = canvas.data.height
    blockSize = canvas.data.blockSize
    maxFlashTime = canvas.data.maxFlashTime
    color = block.color
    streakBoard = canvas.data.streakBoard
    if (color != canvas.data.garbage and block.isFlashing == True):
        if ((int((time.time() - block.timeStartFlashing) * 10) % 2) == 0):
            color = canvas.data.whiteColor
        else:
            color = block.color
    elif (board[row][0].isGarbage == True):
        if ((int((time.time() - block.timeStartFlashing) * 10) % 2) == 0):
            if (col == 0):
                color = canvas.data.garbage
            else:
                color = ""
        else:
            color = block.color
    canvas.create_image(20 + y* blockSize, canvasHeight - 50 - (x+1)*blockSize, image = color, anchor = NW)

def drawBlockAI(canvas, row, col):
    board = canvas.data.AIBoard
    (currentRow, currentCol) = findSelectedBlockAI(canvas)
    width = canvas.data.width
    block = board[row][col]
    x = board[row][col].x
    y = board[row][col].y
    canvasHeight = canvas.data.height
    blockSize = canvas.data.blockSize
    maxFlashTime = canvas.data.maxFlashTime
    color = block.color
    if (color != canvas.data.garbage and block.isFlashing == True):
        if ((int((time.time() - block.timeStartFlashing) * 10) % 2) == 0):
            color = canvas.data.whiteColor
        else:
            color = block.color
    elif (board[row][0].isGarbage == True):
        if ((int((time.time() - block.timeStartFlashing) * 10) % 2) == 0):
            if (col == 0):
                color = canvas.data.garbage
            else:
                color = ""
        else:
            color = block.color
    canvas.create_image(width - 20 - (6*blockSize) + y * blockSize, canvasHeight - 50 - (x+1)*blockSize, image = color, anchor = NW)

def countFlashBlocks(canvas):
    rows = canvas.data.rows
    cols = canvas.data.cols
    board = canvas.data.board
    counter = 0
    for row in xrange(rows):
        for col in xrange(cols):
            if (board[row][col].isFlashing == True):
                counter += 1
    return counter

def drawCursor(canvas):
    rows = canvas.data.rows
    cols = canvas.data.cols
    board = canvas.data.board
    canvasHeight = canvas.data.height
    blockSize = canvas.data.blockSize
    for row in xrange(rows):
        for col in xrange(cols):
            block = board[row][col]
            if (block.isSelected == True):
                canvas.create_rectangle(200 + col * blockSize, canvasHeight - 50 -
                                        (row+1)*blockSize, 200 + (col+1) * blockSize,
                                        canvasHeight - 50 - (row * blockSize), width = 3, outline = "white")
                canvas.create_rectangle(200 + (col+1) * blockSize, canvasHeight - 50
                                        - (row+1)*blockSize, 200 + (col+2) * blockSize,
                                        canvasHeight - 50 - (row * blockSize), width = 3, outline = "white")

def drawCursor2Player(canvas):
    rows = canvas.data.rows
    cols = canvas.data.cols
    board = canvas.data.board
    canvasHeight = canvas.data.height
    blockSize = canvas.data.blockSize
    for row in xrange(rows):
        for col in xrange(cols):
            block = board[row][col]
            if (block.isSelected == True):
                canvas.create_rectangle(20 + col * blockSize, canvasHeight - 50 -
                                        (row+1)*blockSize, 20 + (col+1) * blockSize,
                                        canvasHeight - 50 - (row * blockSize), width = 3, outline = "white")
                canvas.create_rectangle(20 + (col+1) * blockSize, canvasHeight - 50
                    - (row+1)*blockSize, 20 + (col+2) * blockSize, canvasHeight - 50 -
                    (row * blockSize), width = 3, outline = "white")

def drawAICursor(canvas):
    rows = canvas.data.rows
    cols = canvas.data.cols
    board = canvas.data.AIBoard
    width = canvas.data.width
    canvasHeight = canvas.data.height
    blockSize = canvas.data.blockSize
    for row in xrange(rows):
        for col in xrange(cols):
            block = board[row][col]
            if (block.isSelected == True):
                canvas.create_rectangle(width - (6*blockSize) - 20 + col * blockSize,
                                        canvasHeight - 50 - (row+1)*blockSize, width - (6*blockSize) - 20 + (col+1) * blockSize,
                                        canvasHeight - 50 - (row * blockSize), width = 3, outline = "white")
                canvas.create_rectangle(width - (6*blockSize) - 20 + (col+1) * blockSize,
                                        canvasHeight - 50 - (row+1)*blockSize, width - (6*blockSize) - 20 + (col+2) * blockSize,
                                        canvasHeight - 50 - (row * blockSize), width = 3, outline = "white")

def drawGameOver(canvas):
    width = canvas.data.width
    if (canvas.data.VSComScreen == True):
        if (canvas.data.AILost == True):
            canvas.create_text(width / 2, 400, text = "Player wins!", font = ("Helvetica", 50), fill = "white")
        else:
            canvas.create_text(width / 2, 400, text = "COM wins!", font = ("Helvetica", 50), fill = "white")
    else:
        canvas.create_text(width / 2, 400, text="Game Over", font=("Helvetica", 50), fill = "gray")
        #canvas.create_text(width * 3 / 4, 350, text = "0:00", font=("Helvetica", 50), fill = "white")


def drawMenu(canvas):
    canvas.delete(ALL)
    width = canvas.data.width
    height = canvas.data.height
    if (canvas.data.instructionsScreen == True):
        canvas.create_image(0,0,image = canvas.data.instructions, anchor = NW)
    elif (canvas.data.settingsScreen == True):
        canvas.create_image(0,0,image = canvas.data.controls, anchor = NW)
    elif (canvas.data.onePlayerScreen == False):
        canvas.create_rectangle(0,0,width,height,fill = "black")
        canvas.create_text(width/2, height/4, text="Tetreweled", font=("Helvetica", 50), fill = "white")
        canvas.create_text(width/2, height*4/8, text="1 player", font=("Helvetica", 50), fill = "white")
        canvas.create_text(width/2, height*5/8, text="VS Com", font=("Helvetica", 50), fill = "white")
        canvas.create_text(width/2, height*6/8, text="Controls", font=("Helvetica", 50), fill = "white")
        canvas.create_text(width/2, height*7/8, text="Instructions", font=("Helvetica", 50), fill = "white")
    elif (canvas.data.onePlayerScreen == True and canvas.data.marathonScreen == False and canvas.data.timeAttackScreen == False
          and canvas.data.VSComScreen == False and canvas.data.garbageScreen == False):
        canvas.create_rectangle(0,0,width,height,fill = "black")
        canvas.create_text(width/2, height/4, text="Tetreweled", font=("Helvetica", 50), fill = "white")
        canvas.create_text(width/2, height*4/8, text="Marathon", font=("Helvetica", 50), fill = "white")
        canvas.create_text(width/2, height*5/8, text="Time Attack", font=("Helvetica", 50), fill = "white")
        canvas.create_text(width/2, height*6/8, text="Garbage", font=("Helvetica", 50), fill = "white")
        canvas.create_text(width/2, height*7/8, text="Back", font=("Helvetica", 50), fill = "white")
    elif (canvas.data.onePlayerScreen == True and (canvas.data.marathonScreen == True or canvas.data.timeAttackScreen == True
                                                   or canvas.data.VSComScreen == True or canvas.data.garbageScreen == True)):
        canvas.create_rectangle(0,0,width,height,fill = "black")
        canvas.create_text(width/2, height/4, text="Tetreweled", font=("Helvetica", 50), fill = "white")
        canvas.create_text(width/2, height*4/8, text="Easy", font=("Helvetica", 50), fill = "white")
        canvas.create_text(width/2, height*5/8, text="Medium", font=("Helvetica", 50), fill = "white")
        canvas.create_text(width/2, height*6/8, text="Hard", font=("Helvetica", 50), fill = "white")
        canvas.create_text(width/2, height*7/8, text="Back", font=("Helvetica", 50), fill = "white")


# Block class

class Block(object):
    blockSize = 60

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.alive = True
        self.isSelected = False
        self.flag = False
        self.isGrounded = True
        self.isFlashing = False
        self.timeStartFlashing = 0
        self.isGarbage = False

    def swapBlocks(self, other):
        tempAlive = other.alive
        tempIsGrounded = other.isGrounded
        tempFlag = other.flag
        other.alive = self.alive
        other.isGrounded = self.isGrounded
        other.flag = self.flag
        self.alive = tempAlive
        self.isGrounded = tempIsGrounded
        self.flag = tempFlag
        tempColor = other.color
        other.color = self.color
        self.color = tempColor
        tempIsFlashing = other.isFlashing
        tempTimeStartFlashing = other.timeStartFlashing
        other.isFlashing = self.isFlashing
        other.timeStartflashing = self.timeStartFlashing
        self.isFlashing = tempIsFlashing
        self.timeStartFlashing = tempTimeStartFlashing
        tempIsGarbage = other.isGarbage
        other.isGarbage = self.isGarbage
        self.isGarbage = tempIsGarbage
        """
        tempIsSelected = other.isSelected
        other.isSelected = self.isSelected
        self.isSelected = tempIsSelected
        """
    


    def copyBlock(self, other):
        self.alive = other.alive
        self.isGrounded = other.isGrounded
        self.flag = other.flag
        self.color = other.color
        self.isFlashing = other.isFlashing
        self.timeStartFlashing = other.isFlashing


class Garbage(object):
    
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

def initVSCom(canvas):
    canvas.data.countDown = 4
    getImages(canvas)
    canvas.data.board = 0
    canvas.data.rows = 12
    canvas.data.cols = 6
    canvas.data.blockSize = 60
    canvas.data.score = 0
    canvas.data.colors = ["red","blue","yellow", "green", "orange", "red","blue","yellow", "green", "orange", "pink"]
    canvas.data.maxFlashTime = 12
    canvas.data.flashNumber = 0
    canvas.data.startTime = time.time()
    canvas.data.gameTime = time.time()
    canvas.data.gameOver = False
    canvas.data.risingUp = False
    canvas.data.maxTime = 1
    canvas.data.difference = 0
    canvas.data.hasSelectedPowerup = False
    canvas.data.streak = 0
    canvas.data.freezeTime = False
    canvas.data.freezeTimeElapsed = 0
    canvas.data.swappingBlocks = False
    createPowerupsAI(canvas)
    setDifficulty(canvas)
    setAIVariables(canvas)
    canvas.data.scoreToGarbage = 2000 * canvas.data.difficulty
    createBoard2Players(canvas)

def setAIVariables(canvas):
    canvas.data.AIBoard = 0
    canvas.data.startTimeAI = time.time()
    canvas.data.differenceAI = 0
    canvas.data.AIStuff = False
    canvas.data.madeMoveAI = False
    canvas.data.swappingBlockAI = False
    canvas.data.movingToDestination = False
    canvas.data.AIScore = 0

def createPowerupsAI(canvas):
    clearRow = PhotoImage(file = 'clear_row.gif')
    clearCol = PhotoImage(file = 'clear_col.gif')
    freezeTime = PhotoImage(file = 'freeze.gif')
    canvas.data.powerUps = [clearRow, clearCol]
    canvas.data.currentPowerup = []
    canvas.data.currentPowerupAI = []

def initGarbage(canvas):
    canvas.data.countDown = 4
    getImages(canvas)
    loadGarbage(canvas)
    canvas.data.board = 0
    canvas.data.rows = 12
    canvas.data.cols = 6
    canvas.data.blockSize = 60
    canvas.data.score = 0
    canvas.data.colors = ["red","blue","yellow", "green", "orange", "red","blue","yellow", "green", "orange", "pink"]
    canvas.data.maxFlashTime = 12
    canvas.data.flashNumber = 0
    canvas.data.startTime = time.time()
    canvas.data.gameTime = time.time()
    canvas.data.gameOver = False
    canvas.data.risingUp = False
    canvas.data.maxTime = 1
    canvas.data.difference = 0
    canvas.data.streak = 0
    createPowerups(canvas)
    setDifficulty(canvas)
    createBoard(canvas)


def loadGarbage(canvas):
    garbage = PhotoImage(file = 'garbage.gif')
    difficulty = canvas.data.difficulty
    canvas.data.garbage = garbage
    if (difficulty == 3):
        canvas.data.garbageTime = 8
    elif (difficulty == 2):
        canvas.data.garbageTime = 6
    else:
        canvas.data.garbageTime = 4
    
def initMarathon(canvas):
    canvas.data.countDown = 4
    getImages(canvas)
    canvas.data.board = 0
    canvas.data.rows = 12
    canvas.data.cols = 6
    canvas.data.blockSize = 60
    canvas.data.score = 0
    canvas.data.colors = ["red","blue","yellow", "green", "orange", "red","blue","yellow", "green", "orange", "pink"]
    canvas.data.maxFlashTime = 12
    canvas.data.flashNumber = 0
    canvas.data.startTime = time.time()
    canvas.data.gameTime = time.time()
    canvas.data.gameOver = False
    canvas.data.risingUp = False
    canvas.data.maxTime = 1
    canvas.data.difference = 0
    canvas.data.streak = 0
    createPowerups(canvas)
    setDifficulty(canvas)
    createBoard(canvas)

def initTimeAttack(canvas):
    canvas.data.countDown = 4
    canvas.data.maxTimeAttack = 120
    canvas.data.board = 0
    canvas.data.rows = 12
    canvas.data.cols = 6
    canvas.data.blockSize = 60
    canvas.data.score = 0
    canvas.data.colors = ["red","blue","yellow", "green", "orange", "red","blue","yellow", "green", "orange", "pink"]
    getImages(canvas)
    canvas.data.maxFlashTime = 12
    canvas.data.flashNumber = 0
    canvas.data.startTime = time.time()
    canvas.data.gameTime = time.time()
    canvas.data.gameOver = False
    canvas.data.risingUp = False
    canvas.data.maxTime = 1
    canvas.data.difference = 0
    canvas.data.streak = 0
    createPowerups(canvas)
    setDifficulty(canvas)
    createBoard(canvas)
    
def createPowerups(canvas):
    clearRow = PhotoImage(file = 'clear_row.gif')
    clearCol = PhotoImage(file = 'clear_col.gif')
    freezeTime = PhotoImage(file = 'freeze.gif')
    canvas.data.powerUps = [clearRow, clearCol, freezeTime]
    canvas.data.currentPowerup = []
    canvas.data.freezeTime = False
    canvas.data.freezeTimeElapsed = 0
    canvas.data.swappingBlockAI = False
    canvas.data.swappingBlocks = False
    canvas.data.hasSelectedPowerup = False


def getImages(canvas):
    red = PhotoImage(file = 'tile_red.gif')
    blue = PhotoImage(file = 'tile_blue.gif')
    green = PhotoImage(file = 'tile_green.gif')
    orange = PhotoImage(file = 'tile_orange.gif')
    power = PhotoImage(file = 'tile_powerup.gif')
    white = PhotoImage(file = 'tile_white.gif')
    yellow = PhotoImage(file = 'tile_yellow.gif')
    canvas.data.colorImages = [red, blue, yellow, green, orange, red, blue, yellow, green, orange, power]
    canvas.data.powerColor = power
    canvas.data.whiteColor = white
    garbage = PhotoImage(file = 'garbage.gif')
    canvas.data.garbage = garbage

def setDifficulty(canvas):
    difficulty = canvas.data.difficulty
    if (difficulty == 3): # hard
        if (canvas.data.VSComScreen == True):
            canvas.data.timeToRiseAI = 4
            canvas.data.timeBetweenMove = 1
        canvas.data.timeToRise = 4
    elif (difficulty == 2): # medium
        if (canvas.data.VSComScreen == True):
            canvas.data.timeToRiseAI = 6
            canvas.data.timeBetweenMove = 2
        canvas.data.timeToRise = 6
    else: # easy
        if (canvas.data.VSComScreen == True):
            canvas.data.timeToRiseAI = 8
            canvas.data.timeBetweenMove = 3
        canvas.data.timeToRise = 8

def init(canvas):
    canvas.data.difficulty = 0
    canvas.data.menuScreen = True
    canvas.data.onePlayerScreen = False
    canvas.data.marathonScreen = False
    canvas.data.timeAttackScreen = False
    canvas.data.VSComScreen = False
    canvas.data.instructionsScreen = False
    canvas.data.garbageScreen = False
    canvas.data.settingsScreen = False
    canvas.data.instructions = PhotoImage(file = 'instructions.gif')
    canvas.data.controls = PhotoImage(file = 'controls.gif')
    canvas.data.back = False
    canvas.data.gameOver = True
    canvas.data.endTime = 0

def run():
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=1080, height=820)
    canvas.pack()
    root.canvas = canvas.canvas = canvas
    # Set up canvas data and call initMarathon
    class Struct: pass
    canvas.data = Struct()
    canvas.data.width = 1080
    canvas.data.height = 820
    init(canvas) # DK: initMarathon() --> initMarathon(canvas)
    # set up events
    # DK: You can use a local function with a closure
    # to store the canvas binding, like this:
    def f(event): mousePressed(canvas, event)    
    root.bind("<Button-1>", f)
    # DK: Or you can just use an anonymous lamdba function,
    # like this:
    root.bind("<Key>", lambda event: keyPressed(canvas, event))
    timerFired(canvas) # DK: timerFired() --> timerFired(canvas)
    # and launch the app
    root.mainloop()  # This call BLOCKS (so your program waits until you close the window!)
run()
