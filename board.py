from tile import Tile, TILE_RIGHT, TILE_LEFT, TILE_BOTTOM, TILE_TOP

class Board:
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.board = []
    for i in range(0, width):
      temp = []
      for j in range(0, height):
        temp.append(None)
      self.board.append(temp)

  def __iter__(self):
    for row in self.board:
      for tile in row:
        yield tile

  def set_accessible(self, x, y, direction):
    if 0 <= x < self.width and 0 <= y < self.height:
      self.get_tile(x, y).set_accessible(direction, False)

  def fix_accessibility(self):
    for x in range(0, self.width):
      for y in range(0, self.height):
        if self.get_tile(x, y).solid:
          self.set_accessible(x - 1, y, TILE_RIGHT)
          self.set_accessible(x + 1, y, TILE_LEFT)
          self.set_accessible(x, y - 1, TILE_BOTTOM)
          self.set_accessible(x, y + 1, TILE_TOP)

  def set_tile(self, x, y, tile):
    self.board[x][y] = tile

  def get_tile(self, x, y):
    return self.board[x][y]
