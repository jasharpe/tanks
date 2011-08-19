import os, constants, math
from board import Board
from geometry import *
from tile import Tile
from level import Level
import re

def load_level(number, game):
  level_file = open(os.path.join(constants.DATA_DIR, "level%d.dat" % (number)), "r")

  # read from level file, allowing comments starting with '#' and blank lines,
  # returning the first meaningful line, stripped of its new line character.
  def read():
    line = None
    while line is None or line is "" or line.isspace() or line.startswith("#"):
      line = level_file.readline().strip()
    return line

  def process(line):
    return filter(None, re.split("[(), ]", line))

  # board size
  board_size = process(read())
  width = int(board_size[0])
  height = int(board_size[1])

  # player start position
  player_info =  process(read())
  player_start = Point(int(player_info[0]) + 0.5, int(player_info[1]) + 0.5)
  if not (0 <= player_start.x < width) or \
     not (0 <= player_start.y < height):
    raise Exception("Player start position (%d, %d) outside board." % (player_start.x, player_start.y))
  player_direction = int(player_info[2])
  if not 0 <= player_direction < 360:
    raise Exception("Player direction should be between 0 and 359 degrees. Was %d." % player_direction)
  
  # enemies
  start_enemies = read()
  if not start_enemies == "START ENEMIES":
    raise Exception("Excepted 'START ENEMIES' but got %s" % start_enemies)
  enemies = []
  line = None
  while True:
    line = read()
    if line == "END ENEMIES":
      break
    enemy_info = process(line)
    position = Point(int(enemy_info[0]) + 0.5, int(enemy_info[1]) + 0.5)

    if not (0 <= position.x < width) or \
       not (0 <= position.y < height):
      raise Exception("Enemy start position (%d, %d) outside board." % (x, y))

    initial_direction = int(enemy_info[2])
    if not 0 <= initial_direction < 360:
      raise Exception("Initial direction should be between 0 and 359 degrees. Was %d." % initial_direction)
    waypoint_type = enemy_info[3]
    waypoints = []
    for i in xrange(4, len(enemy_info), 2):
      waypoints.append(Point(int(enemy_info[i]) + 0.5, int(enemy_info[i + 1]) + 0.5))
    enemies.append((position, math.pi * initial_direction / 180.0, waypoint_type, waypoints))

  start_powerups = read()
  if not start_powerups == "START POWERUPS":
    raise Exception("Excepted 'START POWERUPS' but got %s" % start_powerups)
  powerups = []
  while True:
    line = read()
    if line == "END POWERUPS":
      break
    powerup_info = process(line)
    position = Point(int(powerup_info[0]) + 0.5, int(powerup_info[1]) + 0.5)
    powerups.append((position))

  # tiles
  board = Board(width, height)
  for i in range(0, height):
    line = read()
    for j in range(0, width):
      tile = Tile(line[j], j, i)
      if tile.solid:
        if i is player_start.y and j is player_start.x:
          raise Exception("Player start position (%d, %d) is inside a solid tile." % (player_start.x, player_start.y))
        for (p, d, waypoint_type, waypoints) in enemies:
          if i is p.y and j is p.x:
            raise Exception("Enemy start position (%d, %d) is inside a solid tile." % (p.x, p.y))
      board.set_tile(j, i, tile)

  # let each tile know if its walls are accessible (i.e., if they are blocked
  # by another tile or not)
  board.fix_accessibility()

  return Level(game, player_start, math.pi * player_direction / 180.0, board, enemies, powerups)
