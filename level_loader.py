import os, constants, math
from board import Board
from geometry import *
from tile import Tile
from level import Level
import re
from powerup import ShieldPowerup, RepairPowerup, SplashPowerup

powerup_type_map = {
    "SHIELD" : ShieldPowerup,
    "REPAIR" : RepairPowerup,
    "SPLASH" : SplashPowerup
}

def load(number_or_file):
  if type(number_or_file) == int:
    level_file = open(os.path.join(constants.DATA_DIR, "level%d.dat" % (number_or_file)), "r")
  else:
    level_file = open(os.path.join(constants.DATA_DIR, number_or_file), "r")
  
  # read from level file, allowing comments starting with '#' and blank lines,
  # returning the first meaningful line, stripped of its new line character.
  def read():
    line = None
    while line is None or line is "" or line.isspace() or line.startswith("#"):
      line = level_file.readline().strip()
    return line

  def process(line):
    return list(filter(None, re.split("[(), ]", line)))

  name = read()

  # board size
  board_size = process(read())
  width = int(board_size[0])
  height = int(board_size[1])

  # player start position
  player_info =  process(read())
  player_start = Point(float(player_info[0]), float(player_info[1]))
  if not (0 <= player_start.x < width) or \
     not (0 <= player_start.y < height):
    raise Exception("Player start position (%d, %d) outside board." % (player_start.x, player_start.y))
  player_direction = float(player_info[2])
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
    position = Point(float(enemy_info[0]), float(enemy_info[1]))

    if not (0 <= position.x < width) or \
       not (0 <= position.y < height):
      raise Exception("Enemy start position (%d, %d) outside board." % (x, y))

    initial_direction = float(enemy_info[2])
    if not 0 <= initial_direction < 360:
      raise Exception("Initial direction should be between 0 and 359 degrees. Was %d." % initial_direction)
    waypoint_type = enemy_info[3]
    waypoints = []
    for i in range(4, len(enemy_info), 2):
      waypoints.append(Point(float(enemy_info[i]), float(enemy_info[i + 1])))
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
    powerup_type = powerup_info[0]
    position = Point(float(powerup_info[1]), float(powerup_info[2]))
    powerups.append(powerup_type_map[powerup_type](position, powerup_type))

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

  return (name, player_start, player_direction, board, enemies, powerups)

def load_level(number, game):
  (name, player_start, player_direction, board, enemies, powerups) = load(number)
  player_direction_radians = math.pi * player_direction / 180.0
  return Level(name, game, player_start, player_direction_radians, board, enemies, powerups)
