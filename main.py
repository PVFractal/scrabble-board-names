# Imports for the program
# *******************************************************************************************************
import imagemaker
import numpy as np

# Constants/controls for the program
# *******************************************************************************************************

# The goal for the aspect ratio of the board, width/height
ratio = 1.5/1

# The assumed density of the letters of the board, letters/empty spaces
letterDensity = 1/3

# The value multiplier of the ratio score
ratioMultiplier = 1.5

# The penalty if the boundary size increased
ratioBoundaryPenalty = 0.5

# The matching group score
groupScore = 1

# The distance measured between names that cannot match for them to be scored
proximityDistance = 10

# The proximity score multiplier
proximityScoreMultiplier = 1

# How many moves the program will look ahead. Increasing this number exponentially increases the time it takes
movesAhead = 4

# Program setup
# *******************************************************************************************************

# Creating the input. The numbers associated with the names are for grouping.
# The program will attempt to group names with the same numbers, if possible.

# NOTE: Do not use 0 for the group number
input = []

input.append(('Jill', 1))
input.append(('Steve', 1))

input.append(('Brandon', 2))
input.append(('Nina', 2))
input.append(('Greyson', 2))
input.append(('Brody', 2))

input.append(('Tessa', 3))
input.append(('Mason', 3))
input.append(('Hayes', 3))

input.append(('Morgan', 4))
input.append(('Brittany', 4))
input.append(('Stella', 4))

input.append(('Michael', 5))
input.append(('Courtney', 5))
input.append(('Nashville', 5))
input.append(('Paisley', 5))
input.append(('Brixley', 5))

input.append(('Bailey', 6))
input.append(('Joey', 6))
input.append(('Oakley', 6))

input.append(('Lindsay', 7))
input.append(('Peter', 7))

input.append(('Stephany', 8))
input.append(('Matt', 8))
input.append(('Lilly', 8))
input.append(('Emma', 8))
input.append(('Hunter', 8))

input.append(('Joey', 9))
input.append(('Ashton', 9))
input.append(('Thad', 9))
input.append(('Penelope', 9))

input.append(('Steven', 10))

class ScrabbleSolver:


  def run(self, input):
    self.setup(input)

    for singleInput in self.input:
      self.createGridFromWord(singleInput)
      self.resetGrid()
  
  def setup(self, input):
    self.input = []
    # Converting all names to uppercase
    for i in range(len(input)):
      self.input.append((input[i][0].upper(), input[i][1]))

    # Now that input has been made, we shall set up a grid for the letters
    # It shall be three times the size  of the predicted board

    # Counting the letters in the input
    totalLetters = 0
    for (name, _) in self.input:
      totalLetters += len(name)

    # Now that we have the total letter count, we can find the board area
    boardArea = totalLetters / letterDensity

    # Now we must find the dimensions of the board
    self.height = round(np.sqrt(boardArea / ratio) * 3)
    self.width = round(self.height * ratio)

    # Now, we fill in the grid with blanks
    self.resetGrid()

    # Some variables to keep track of the current board size
    self.boardLeft = 0
    self.boardTop = 0
    self.boardRight = 0
    self.boardBottom = 0

  def createGridFromWord(self, word):
    # Defining a dictionary used to keep track of which words we've used
    usedDict = {}

    # Putting the first word into the center of the grid
    xCoord = round(self.width / 2)
    yCoord = round(self.height / 2)
    self.insertWord(word, xCoord, yCoord, 'r')

    # Putting the word into the dictionary
    usedDict[word[0] + str(word[1])] = (xCoord, yCoord, 'r', len(word[0]))

    # Updating the board variables
    self.setBoundaries(usedDict)

    self.runIterations(usedDict)

    self.printGrid(usedDict)

    exportedGrid = self.exportGrid(usedDict)
    imagemaker.drawBoard(exportedGrid, word[0] + str(word[1]) + '_scrabble_board.png')

  def runIterations(self, usedDict):

    while(True):
      # Getting the list of all the best additions we can add with (currently 3) words
      additionList = []
      self.addWord(usedDict, [], additionList)

      # Exiting the loop if there is nothing to add
      if len(additionList) == 0:
        break
      if len(additionList[0]) == 0:
        break
      
      # Looping through the list, finding the best combination
      bestScore = -1
      bestIndex = -1
      for i in range(len(additionList)):
        score = 0
        for additionSequence in additionList[i]:
          score += additionSequence[4]

        if (score > bestScore):
          bestScore = score
          bestIndex = i

      self.addPlacementSet(usedDict, additionList[bestIndex])

    
  
  def addWord(self, usedDict, shortList, longList):
    if (len(shortList) > movesAhead - 1):
      longList.append(shortList.copy())
      return

    self.setBoundaries(usedDict)

    # Finding the best placement for each word we haven't used
    bestPlacementsList = []
    for word in self.input:
      if word[0] + str(word[1]) not in usedDict:
        placement = self.getBestPlacement(usedDict, word)
        score = placement[4]
        if (score > 0):
          bestPlacementsList.append(placement)

    if (len(bestPlacementsList) == 0):
      longList.append(shortList.copy())
      return

    # Next, going and placing each word in the list, trying it out
    for placement in bestPlacementsList:
      word, x, y, direction, score = placement

      # Placing the word on the grid
      deleteString = self.insertWord(word, x, y, direction)
      # Adding it to the dictionary
      usedDict[word[0] + str(word[1])] = (x, y, direction, len(word[0]))

      shortList.append(placement)
      self.addWord(usedDict, shortList, longList)
      shortList.pop(len(shortList) - 1)


      # Deleting the word from the grid
      self.deleteWord(deleteString, x, y, direction)
      # Deleting the word from the dictionary
      del usedDict[word[0] + str(word[1])]



  def getBestPlacement(self, usedDict, word):
    bestPlacement = (-1, -1, -1, -1, -1)
    bestPlacementScore = -1

    # Looping through the words on the board
    for key in usedDict:
      # Looping through the letters of the word
      x, y, direction, length = usedDict[key]
      for _ in range(length):
        gridLetter = self.grid[x][y][0]
        
        # Now checking the letter against each one in the word
        for i in range(len(word[0])):
          if (word[0][i] == gridLetter):
            # We have found a possible place, now we need to check the word in that position
            newWordXCoord = 0
            newWordYCoord = 0
            newDirection = ''
            if (direction == 'r'):
              newWordXCoord = x
              newWordYCoord = y + i
              newDirection = 'd'
            else:
              newWordXCoord = x - i
              newWordYCoord = y
              newDirection = 'r'
            wordOK = self.checkWord(word, newWordXCoord, newWordYCoord, newDirection)
            if (wordOK):
              # If the word fits onto the board with no conflicts, then we score it
              score = self.scoreWord(usedDict, word, newWordXCoord, newWordYCoord, newDirection)

              # We are getting the words with the best scores, so if we have a collection of words, but find one with a better score,
              # then we must get rid of the list
              if (score > bestPlacementScore):
                bestPlacementScore = score
                bestPlacement = (word, newWordXCoord, newWordYCoord, newDirection, score)

        if (direction == 'r'):
          x += 1
        else:
          y -= 1
      

    return bestPlacement

  def checkWord(self, word, startingX, startingY, direction):
    x = startingX
    y = startingY
    for letter in word[0]:
      # Return false if the coordinate is out-of-bounds
      if not self.coordOK(x, y): return False

      gridLetter = self.grid[x][y][0]

      # Checking the squares off to the side
      offXCoord1 = 0
      offYCoord1 = 0
      offXCoord2 = 0
      offYCoord2 = 0

      oppositeDirection = ''

      if (direction == 'r'):
        offXCoord1 = x
        offYCoord1 = y + 1
        offXCoord2 = x
        offYCoord2 = y - 1
        oppositeDirection = 'd'
      else:
        offXCoord1 = x + 1
        offYCoord1 = y
        offXCoord2 = x - 1
        offYCoord2 = y
        oppositeDirection = 'r'

      if (self.coordOK(offXCoord1, offYCoord1)):
        if self.grid[offXCoord1][offYCoord1][2] == direction:
          # We are next to a parallel word
          return False
        elif self.grid[offXCoord1][offYCoord1][2] == oppositeDirection and gridLetter == '':
          # We are next to a perpendicular word that we are not connected to
          return False
        
      if (self.coordOK(offXCoord2, offYCoord2)):
        if self.grid[offXCoord2][offYCoord2][2] == direction:
          # We are next to a parallel word
          return False
        elif self.grid[offXCoord2][offYCoord2][2] == oppositeDirection and gridLetter == '':
          # We are next to a perpendicular word that we are not connected to
          return False

      if gridLetter != '':
        if gridLetter != letter or self.grid[x][y][2] == direction:
          # There is a mismatch with another word
          return False

      if direction == 'r':
        x += 1
      else:
        y -= 1
    

    # Checking one letter in front of the word
    lenR = 0
    lenD = 0
    if direction == 'r': lenR = 1
    if direction == 'd': lenD = 1
    if self.coordOK(startingX - lenR, startingY + lenD): 
      if self.grid[startingX - lenR][startingY + lenD][0] != '': return False

    # Checking one more letter beyond the word
    if self.coordOK(x, y): 
      if self.grid[x][y][0] != '': return False
    

    # The word checks out, so we return true
    return True

  def scoreWord(self, usedDict, word, startingX, startingY, direction):
    score = 0

    x = startingX
    y = startingY
    for letter in word[0]:
      gridLetter = self.grid[x][y][0]
      gridGroup = self.grid[x][y][1]

      # Adding score for each word we intersect in the group
      if gridLetter == letter and gridGroup == word[1]:
        score += groupScore
        
      if direction == 'r':
        x += 1
      else:
        y -= 1
    ratioScore = self.scoreWordRatioChanges(startingX, startingY, direction, len(word[0]))

    proximityScore = self.scoreWordProximity(usedDict, word, startingX, startingY, direction)
    
    return score + (ratioScore * ratioMultiplier) + (proximityScore * proximityScoreMultiplier)


  def coordOK(self, x, y):
    if (x >= 0 and x < self.width) and (y >= 0 and y < self.height): return True
    return False


  def scoreRatio(self):
    boardHeight = self.boardTop - self.boardBottom
    boardWidth = self.boardRight - self.boardLeft
    currentRatio = boardWidth/boardHeight

    if (ratio > currentRatio):
      return currentRatio / ratio
    else: 
      return ratio / currentRatio

  def scoreWordRatioChanges(self, startingX, startingY, direction, length):

    lengthR = 0
    lengthD = 0
    if (direction == 'r'):
      lengthR = length
    else:
      lengthD = length

    boundaryChanged = False

    # Getting what the new boundaries of the board would be if a word was added
    newBoardLeft = 0
    newBoardTop = 0
    newBoardRight = 0
    newBoardBotom = 0

    if self.boardLeft < startingX:
      newBoardLeft = self.boardLeft
    else:
      newBoardLeft = startingX
      boundaryChanged = True
    
    if self.boardTop > startingY:
      newBoardTop = self.boardTop
    else:
      newBoardTop = startingY
      boundaryChanged = True

    if self.boardRight > startingX + lengthR:
      newBoardRight = self.boardRight
    else:
      newBoardRight = startingX + lengthR
      boundaryChanged = True

    if self.boardBottom < startingY - lengthD:
      newBoardBotom = self.boardBottom
    else:
      newBoardBotom = startingY - lengthD
      boundaryChanged = True
    

    penalty = 0
    # Adding a penalty if the boundary increased in size
    if boundaryChanged: 
      penalty = ratioBoundaryPenalty


    boardHeight = newBoardTop - newBoardBotom
    boardWidth = newBoardRight - newBoardLeft
    currentRatio = boardWidth/boardHeight
    if (ratio > currentRatio):
      return (currentRatio / ratio) - penalty
    else: 
      return (ratio / currentRatio) - penalty

  def scoreWordProximity(self, usedDict, word, startingX, startingY, direction):
    proximityScore = 0
    # Looping through the dict
    for key in usedDict:
      # Getting the dictionary placement
      x, y, placedDirection, placementLength = usedDict[key]
      # Getting the group number
      group = self.grid[x][y][1]

      # Checking to see if the group is the same
      if group == word[1]:
        # Now, checking to see if they intersect. If they don't, then we can score based on proximity at least

        canScore = True
        
        if direction != placedDirection:
          if direction == 'r':
            if (x >= startingX and x <= startingX + len(word[0])) and (y >= startingY and y - placementLength <= startingY):
              canScore = False
          else:
            if (x <= startingX and x + placementLength >= startingX) and (y >= startingY - len(word[0]) and y <= startingY):
              canScore = False

        
        if canScore:
          # Getting the distance
          xDist = startingX - x
          yDist = startingY - y
          dist = np.sqrt(xDist * xDist + yDist * yDist)

          if (dist < proximityDistance):
            proximityScore += (proximityDistance - dist) / proximityDistance

    return proximityScore


  def setBoundaries(self, usedDict):

    # Resetting to defaults
    self.boardBottom = -1
    self.boardTop = -1
    self.boardLeft = -1
    self.boardRight = -1

    for key in usedDict:
      x, y, direction, length = usedDict[key]
      lengthR = 0
      lengthD = 0
      if (direction == 'r'):
        lengthR = length
      else:
        lengthD = length
      
      # If the values are -1, then set them to the first word
      if (self.boardRight == -1):
        self.boardRight = x + lengthR
      if (self.boardLeft == -1):
        self.boardLeft = x
      if (self.boardTop == -1):
        self.boardTop = y
      if (self.boardBottom == -1):
        self.boardBottom = y - lengthD
      
      # Expanding the boundary if we need to
      self.boardLeft = self.boardLeft if self.boardLeft < x else x
      self.boardTop = self.boardTop if self.boardTop > y else y
      self.boardRight = self.boardRight if self.boardRight > x + lengthR else x + lengthR
      self.boardBottom = self.boardBottom if self.boardBottom < y - lengthD else y - lengthD

  def insertWord(self, word, startingX, startingY, direction):
    # For the deleteWord function.
    # This will keep track of exactly which characters were added, so that they can be deleted later.
    # We wouldn't want to delete letters from another word if this word crosses it
    deleteString = ''

    x = startingX
    y = startingY
    for letter in word[0]:
      
      if (self.grid[x][y][0] == ''):
        deleteString += '1'
        self.grid[x][y] = (letter, word[1], direction)
      else:
        deleteString += '0'

      if (direction == 'r'):
        x += 1
      else:
        y -= 1
    
    return deleteString
  
  def deleteWord(self, deleteString, startingX, startingY, direction):
    x = startingX
    y = startingY
    for letter in deleteString:
      
      if letter == '1':
        self.grid[x][y] = ('', 0, '')

      if (direction == 'r'):
        x += 1
      else:
        y -= 1
    
    return deleteString

  def addPlacementSet(self, usedDict, placementSet):
    for placement in placementSet:
      word, x, y, direction, score = placement
      # Placing the word on the grid
      self.insertWord(word, x, y, direction)
      # Adding it to the dictionary
      usedDict[word[0] + str(word[1])] = (x, y, direction, len(word[0]))

      break # Added this in later, will probably make the algorithm better to look ahead, but only place the first in the set

  def resetGrid(self):
    self.grid = []
    for _ in range(self.width):
      column = []
      for _ in range(self.height):
        column.append(('', 0, ''))
      self.grid.append(column)


  def printGrid(self, usedDict):
    self.setBoundaries(usedDict)
    gridString = ''
    for y in range(self.boardTop, self.boardBottom - 1, -1):
      for x in range(self.boardLeft, self.boardRight + 1):
        if (self.grid[x][y][0] == ''):
          gridString += ' '
        else:
          gridString += self.grid[x][y][0]
      gridString += '\n'
    print(gridString)
  
  def exportGrid(self, usedDict):
    self.setBoundaries(usedDict)
    gridCopy = []
    for x in range(self.boardLeft, self.boardRight):
      gridColumn = []
      for y in range(self.boardTop, self.boardBottom, -1):
        gridColumn.append(self.grid[x][y][0])
      gridCopy.append(gridColumn)
    return gridCopy


solver = ScrabbleSolver()
solver.run(input)