import pygame
import constants
from board import Board
from tile import Tile, TILE_RIGHT, TILE_LEFT, TILE_BOTTOM, TILE_TOP
from geometry import Vector, Point, Line, ORIGIN
from tank import Tank, Turret
from bullet import BOUNCED, EXPLODED
from explosion import Explosion, Shockwave

def load_level(number):
  level_file = open("levels/level%d.dat" % (number), "r")
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

class Level:
  def __init__(self, player_start_x, player_start_y, board):
    self.player_start = Point(player_start_x, player_start_y)
    self.board = board

    self.tanks = pygame.sprite.RenderPlain()
    self.turrets = pygame.sprite.RenderPlain()

    self.player = Tank(self.player_start.x, self.player_start.y)
    self.tanks.add(self.player)
    self.turret = Turret(self.player)
    self.turrets.add(self.turret)

    self.tiles = pygame.sprite.RenderPlain()
    for tile in self.board:
      self.tiles.add(tile)
    self.solid = pygame.sprite.RenderPlain()
    self.non_solid = pygame.sprite.RenderPlain()
    for tile in self.tiles:
      if tile.solid:
        self.solid.add(tile)
      else:
        self.non_solid.add(tile)
    self.bullets = pygame.sprite.RenderPlain()
    self.shockwaves = pygame.sprite.RenderPlain()
    self.explosions = pygame.sprite.RenderPlain()

  def update_controls(self, events, pressed, mouse):
    self.events = events
    self.pressed = pressed
    self.mouse = mouse

  def update(self, delta):
    fire = False
    for event in self.events:
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        fire = True

    pressed = self.pressed
    if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
      self.player.turn_left(delta)
    elif pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
      self.player.turn_right(delta)
    if pressed[pygame.K_UP] or pressed[pygame.K_w]:
      self.player.accelerate(delta)
    elif pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
      self.player.decelerate(delta)
    else:
      self.player.neutral(delta)

    self.tanks.update(delta)
    if self.player.collides_with_tile(self.solid):
      self.player.revert()

    # turret control
    # mouse position
    m_p = self.mouse
    self.turret.turn(delta, Point(float(m_p[0]) / constants.TILE_SIZE, float(m_p[1]) / constants.TILE_SIZE))

    self.turrets.update(delta)
    self.bullets.update(delta)
    self.shockwaves.update(delta)
    self.explosions.update(delta)

    for shockwave in self.shockwaves:
      if shockwave.age > constants.SHOCKWAVE_DURATION:
        shockwave.remove(self.shockwaves)

    for explosion in self.explosions:
      if explosion.age > constants.EXPLOSION_DURATION:
        explosion.remove(self.explosions)

    # fire!
    if fire:
      bullet = self.turret.fire()
      if not bullet is None:
        self.bullets.add(bullet)

    # do bullet collision detection
    # bounce off walls once, then explode on second contact
    
    for bullet in self.bullets:
      if bullet.total_distance > constants.BULLET_MAX_RANGE:
        self.explosions.add(Explosion(bullet.position.x, bullet.position.y))
        bullet.remove(self.bullets)
        bullet.die()
      else:
        results = bullet.bounce(self.solid)
        for (result, position) in results:
          if result == EXPLODED:
            self.explosions.add(Explosion(position.x, position.y))
            bullet.remove(self.bullets)
            bullet.die()
          elif result == BOUNCED:
            self.shockwaves.add(Shockwave(position.x, position.y))

  def draw(self, screen):
    self.non_solid.draw(screen)
    self.tanks.draw(screen)
    self.turrets.draw(screen)
    self.shockwaves.draw(screen)
    self.explosions.draw(screen)
    self.solid.draw(screen)
    self.bullets.draw(screen)
