from PIL import Image, ImageDraw, ImageFont

def drawBoard(grid, name):

  # Exiting if nothing provided
  if len(grid) == 0: return
  if len(grid[0]) == 0: return

  # Assigning constants
  width = len(grid)
  height = len(grid[0])
  squareSize = 50
  font = ImageFont.truetype('fonts/tnrbold.ttf', squareSize / 1.6)
  # font = ImageFont.load_default(squareSize / 1.6)

  # Color constants
  boardColor = (168, 98, 50)
  scrabbleFill = (240, 200, 144)
  textColor = (41, 33, 21)

  # Creating the image
  img = Image.new("RGB", ((width + 2) * squareSize, (height + 2) * squareSize), boardColor)
  draw = ImageDraw.Draw(img)

  # Looping through the grid, drawing the squares
  for x in range(width):
    for y in range(height):
      if (grid[x][y] != ''):
        # Drawing the square
        xLeft = (x + 1) * squareSize
        yTop = (y + 1) * squareSize
        coords = (xLeft, yTop, xLeft + squareSize, yTop + squareSize)
        draw.rectangle(coords, fill=scrabbleFill, outline=textColor, width=2)

        # Drawing the text
        textPosition = (xLeft + (squareSize / 4), yTop + (squareSize / 4) - (squareSize / 10))
        draw.text(textPosition, grid[x][y], fill=textColor, font=font)
        
  
  
  img.save('images/' + name)
