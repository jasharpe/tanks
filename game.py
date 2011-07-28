import pygame
import constants, math
from tank import Tank, Turret
from geometry import Vector, Point, Line, ORIGIN
from tile import Tile, TILE_RIGHT, TILE_LEFT, TILE_BOTTOM, TILE_TOP

FPS = 60

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
    for x in xrange(0, self.width):
      for y in xrange(0, self.height):
        if self.get_tile(x, y).solid:
          self.set_accessible(x - 1, y, TILE_RIGHT)
          self.set_accessible(x + 1, y, TILE_LEFT)
          self.set_accessible(x, y - 1, TILE_BOTTOM)
          self.set_accessible(x, y + 1, TILE_TOP)

  def set_tile(self, x, y, tile):
    self.board[x][y] = tile

  def get_tile(self, x, y):
    return self.board[x][y]

class Level:
  def __init__(self, player_start_x, player_start_y, board):
    self.player_start = Vector(player_start_x, player_start_y)
    self.board = board

def load_level(number):
  level_file = open("level%d.dat" % (number), "r")
  player_start_x = int(level_file.readline().strip())
  player_start_y = int(level_file.readline().strip())
  height = int(level_file.readline().strip())
  width = int(level_file.readline().strip())
  board = Board(width, height)
  for i in range(0, height):
    line = level_file.readline().strip()
    for j in range(0, width):
      board.set_tile(j, i, Tile(line[j], j, i))
  board.fix_accessibility()
  return Level(player_start_x, player_start_y, board)

def tank_collides_with_tile(tank, tile):
  # if the rects don't even collide, then they don't collide
  if not pygame.sprite.collide_rect(tank, tile):
    return []
  
  # otherwise, have to verify collision in case of turned tank
  half_width = constants.TANK_SIZE_RATIO / 2
  half_height = constants.TANK_SIZE_RATIO / 2
  minus_center = ORIGIN - tank.position
  plus_center = tank.position - ORIGIN
  back_left = tank.position.translate(Vector(-half_width, -half_height)).translate(minus_center).rotate(tank.direction).translate(plus_center)
  front_left = tank.position.translate(Vector(half_width, -half_height)).translate(minus_center).rotate(tank.direction).translate(plus_center)
  back_right = tank.position.translate(Vector(-half_width, half_height)).translate(minus_center).rotate(tank.direction).translate(plus_center)
  front_right = tank.position.translate(Vector(half_width, half_height)).translate(minus_center).rotate(tank.direction).translate(plus_center)
  front = Line(front_left, front_right)
  back = Line(back_left, back_right)
  left = Line(back_left, front_left)
  right = Line(back_right, front_right)
  sides = [front, back, left, right]

  tile_top_left = tile.position.translate(Vector(-0.5, -0.5))
  tile_top_right = tile.position.translate(Vector(0.5, -0.5))
  tile_bottom_right = tile.position.translate(Vector(0.5, 0.5))
  tile_bottom_left = tile.position.translate(Vector(-0.5, 0.5))
  tile_left = Line(tile_top_left, tile_bottom_left)
  tile_right = Line(tile_top_right, tile_bottom_right)
  tile_top = Line(tile_top_right, tile_top_left)
  tile_bottom = Line(tile_bottom_right, tile_bottom_left)
  tile_sides = [tile_left, tile_right, tile_top, tile_bottom]

  intersects = []
  for side in sides:
    for tile_side in tile_sides:
      p = side.intersect_segments(tile_side)
      if not p is None:
        intersects.append((side, tile_side, p))

  return intersects

def main():
  pygame.init()
  screen = pygame.display.set_mode(
      [constants.RESOLUTION_X, constants.RESOLUTION_Y])
  pygame.display.set_caption('Tanks!')

  level = load_level(1)

  tanks = pygame.sprite.RenderPlain()
  turrets = pygame.sprite.RenderPlain()

  player = Tank(level.player_start.x, level.player_start.y)
  tanks.add(player)
  turret = Turret(player)
  turrets.add(turret)

  tiles = pygame.sprite.RenderPlain()
  for tile in level.board:
    tiles.add(tile)
  solid = pygame.sprite.RenderPlain()
  for tile in tiles:
    if tile.solid:
      solid.add(tile)
  bullets = pygame.sprite.RenderPlain()
  shocks = pygame.sprite.RenderPlain()
  explosions = pygame.sprite.RenderPlain()

  clock = pygame.time.Clock()
  exit_program = False
  while True:
    delta = clock.tick(FPS)

    # update

    # event handling
    fire = False
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        exit_program = True
      elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        fire = True
    
    # control handling
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
      player.turn_left(delta)
    elif pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
      player.turn_right(delta)
    if pressed[pygame.K_UP] or pressed[pygame.K_w]:
      player.accelerate(delta)
    elif pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
      player.decelerate(delta)
    else:
      player.neutral(delta)

    if exit_program:
      break
   
    tanks.update(delta)
    for tile in solid:
      intersects = tank_collides_with_tile(player, tile)
      if len(intersects) > 0:
        player.revert()

    # turret control
    # mouse position
    m_p = pygame.mouse.get_pos()
    turret.turn(delta, Point(float(m_p[0]) / constants.TILE_SIZE, float(m_p[1]) / constants.TILE_SIZE))

    turrets.update(delta)
    bullets.update(delta)

    # fire!
    if fire:
      bullet = turret.fire()
      if not bullet is None:
        bullets.add(bullet)

    # do bullet collision detection
    # bounce off walls once, then explode on second contact
    
    for bullet in bullets:
      bullet.bounce(solid)       

    # draw

    screen.fill((0, 0, 0))
    tiles.draw(screen)
    tanks.draw(screen)
    bullets.draw(screen)
    turrets.draw(screen)

    pygame.display.flip()

  pygame.quit()

if __name__ == "__main__":
  main()
