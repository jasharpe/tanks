import pygame, os
import constants
from ai import *
from board import Board
from tile import Tile, TILE_RIGHT, TILE_LEFT, TILE_BOTTOM, TILE_TOP
from geometry import Vector, Point, Line, ORIGIN
from tank import Tank, Turret, TANK_EXPLODED
from bullet import BOUNCED, EXPLODED
from explosion import Explosion, Shockwave
from sound import play_sound
from game_event import RestartLevelEvent, AdvanceLevelEvent
from powerup import Powerup
from collision import *
from particle import *
from shield import Shield
import utils

LEVEL_ONGOING = 1
LEVEL_BEATEN = 2
LEVEL_LOST = 3

class TimedLevelAdvance:
  def __init__(self, time, level):
    self.level = level
    self.time_left = time

  def update(self, delta):
    self.time_left -= delta
    self.time_left = max(0, self.time_left)
    if self.time_left == 0:
      self.level.game.register_event(AdvanceLevelEvent(self.level))

class TimedLevelRestart:
  def __init__(self, time, level):
    self.level = level
    self.time_left = time

  def update(self, delta):
    self.time_left -= delta
    self.time_left = max(0, self.time_left)
    if self.time_left == 0:
      self.level.game.register_event(RestartLevelEvent(self.level))
      return True
    return False

class Level:
  def __init__(self, game, player_start, player_direction, board, enemies):
    self.game = game

    self.player_start = player_start
    self.player_direction = player_direction
    self.board = board

    self.powerups = pygame.sprite.RenderPlain()
    self.powerups.add(Powerup(2, 2))

    self.shields = pygame.sprite.RenderPlain()

    self.powerup_particles = pygame.sprite.RenderPlain()
    self.trail_particles = pygame.sprite.RenderPlain()

    self.tanks = pygame.sprite.RenderPlain()
    self.turrets = pygame.sprite.RenderPlain()

    self.player = Tank(self.player_start, self.player_direction)
    self.tanks.add(self.player)
    self.turret = Turret(self.player)
    self.turrets.add(self.turret)

    self.enemies = pygame.sprite.RenderPlain()
    self.enemy_turrets = pygame.sprite.RenderPlain()
    self.enemy_ai = []
    self.enemy_turret_ai = []
    for (p, d, waypoint_type, waypoints) in enemies:
      enemy = Tank(p, d, constants.ENEMY_TANK_COLOR)
      self.enemy_ai.append(TankAI(enemy, self, waypoints, waypoint_type))
      enemy_turret = Turret(enemy)
      self.enemies.add(enemy)
      self.enemy_turrets.add(enemy_turret)
      self.enemy_turret_ai.append(TurretAI(enemy_turret, self))

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
    self.old_status = LEVEL_ONGOING
    self.text = None

    self.timers = []

    self.paused = False
  
  def get_status(self):
    if not self.enemies:
      return LEVEL_BEATEN
    if self.player.dead:
      return LEVEL_LOST
    return LEVEL_ONGOING

  def update(self, delta, events, pressed, mouse):
    for event in events:
      if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
        self.paused = not self.paused
    
    # if paused, don't update this frame
    if self.paused:
      return

    fire = False
    for event in events:
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        fire = True

    if not self.player.dead:
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
      if tank_collides_with_tile(self.player, self.solid):
        self.player.revert()
      # this is fancy and kind of nice, but hard! and looks jittery
      #intersects = self.player.collides_with_tile(self.solid)
      #if intersects:
      #  for (side, tile_side, p) in intersects:
      #    self.player.push_out(delta, side, tile_side, p)
      #    if not self.player.collides_with_tile(self.solid):
      #      break
      #  if self.player.collides_with_tile(self.solid):
      #    self.player.revert()
      #  else:
      #    self.player.speed = min(0.2, self.player.speed)

    # AI control of enemy tanks
    self.enemy_ai = filter(lambda x: x.tank in self.enemies, self.enemy_ai)
    for enemy_ai in self.enemy_ai:
      enemy_ai.control(delta)

    # update enemies
    self.enemies.update(delta)
    for enemy in self.enemies:
      if tank_collides_with_tile(enemy, self.solid):
        enemy.revert()

    # check for tank to tank collisions
    for enemy in self.enemies:
      if not self.player.dead and tank_collides_with_tank(enemy, self.player):
        self.player.revert()
        enemy.revert()

    # turret AI
    self.enemy_turret_ai = filter(lambda x: x.turret in self.enemy_turrets, self.enemy_turret_ai)
    for turret_ai in self.enemy_turret_ai:
      bullet = turret_ai.control(delta)
      if bullet is not None:
        play_sound("fire")
        self.bullets.add(bullet)

    # turret control
    # mouse position
    m_p = mouse
    if not self.player.dead:
      self.turret.turn(delta, Point(float(m_p[0]) / constants.TILE_SIZE, float(m_p[1]) / constants.TILE_SIZE))

      # fire!
      if fire:
        bullet = self.turret.fire()
        if not bullet is None:
          play_sound("fire")
          self.bullets.add(bullet)

    self.enemy_turrets.update(delta)
    self.turrets.update(delta)
    self.bullets.update(delta)
    self.shockwaves.update(delta)
    self.explosions.update(delta)
    self.powerups.update(delta)
    self.powerup_particles.update(delta)
    self.trail_particles.update(delta)
    self.shields.update(delta)

    for particle in self.powerup_particles:
      if particle.age >= particle.max_age:
        particle.remove(self.powerup_particles)

    for particle in self.trail_particles:
      if particle.age >= particle.max_age:
        particle.remove(self.trail_particles)


    for shockwave in self.shockwaves:
      if shockwave.age > constants.SHOCKWAVE_DURATION:
        shockwave.remove(self.shockwaves)

    for explosion in self.explosions:
      if explosion.age > constants.EXPLOSION_DURATION:
        explosion.remove(self.explosions)

    # do bullet collision detection
    # bounce off walls once, then explode on second contact
    for bullet in self.bullets:
      # check for bullet/tank collisions
      if bullet.dead: continue

      if not self.player.dead and bullet_collides_with_tank(bullet, self.player):
        # do something to the player
        result = self.player.hurt()
        if result is TANK_EXPLODED:
          play_sound("tank_explode")
          self.explosions.add(Explosion(self.player.position.x, self.player.position.y, constants.BIG_EXPLOSION_MAX_RATIO, constants.BIG_EXPLOSION_MIN_RATIO))
          self.player.remove(self.tanks)
          self.player.turret.remove(self.turrets)
        else:
          play_sound("bullet_explode")

        # explode the bullet
        self.explosions.add(Explosion(bullet.position.x, bullet.position.y))
        bullet.remove(self.bullets)
        bullet.die()
      if bullet.dead: continue

      for enemy in self.enemies:
        if bullet_collides_with_tank(bullet, enemy):
          # damage the enemy
          result = enemy.hurt()
          if result is TANK_EXPLODED:
            play_sound("tank_explode")
            self.explosions.add(Explosion(enemy.position.x, enemy.position.y, constants.BIG_EXPLOSION_MAX_RATIO, constants.BIG_EXPLOSION_MIN_RATIO))
            enemy.remove(self.enemies)
            enemy.turret.remove(self.enemy_turrets)
          else:
            play_sound("bullet_explode")

          # explode the bullet
          self.explosions.add(Explosion(bullet.position.x, bullet.position.y))
          bullet.remove(self.bullets)
          bullet.die()
          break
      if bullet.dead: continue

      # check for bullet/bullet collisions
      for bullet2 in filter(lambda x: x is not bullet, self.bullets):
        if bullet_collides_with_bullet(bullet, bullet2):
          play_sound("bullet_explode")
          self.explosions.add(Explosion(bullet.position.x, bullet.position.y))
          bullet.remove(self.bullets)
          bullet.die()
          self.explosions.add(Explosion(bullet2.position.x, bullet2.position.y))
          bullet2.remove(self.bullets)
          bullet2.die()
      if bullet.dead: continue

      # check for bullets reaching max range
      if bullet.total_distance > constants.BULLET_MAX_RANGE:
        play_sound("bullet_explode")
        self.explosions.add(Explosion(bullet.position.x, bullet.position.y))
        bullet.remove(self.bullets)
        bullet.die()
      # check for bullet bounces or wall collisions
      else:
        results = bullet.bounce(self.solid)
        for (result, position) in results:
          if result == EXPLODED:
            play_sound("bullet_explode")
            self.explosions.add(Explosion(bullet.old_position.x, bullet.old_position.y))
            bullet.remove(self.bullets)
            bullet.die()
          elif result == BOUNCED:
            play_sound("pong", 0.35)
            self.shockwaves.add(Shockwave(position.x, position.y))
      if bullet.dead: continue

    # apply powerups
    for powerup in self.powerups:
      if not powerup.taken:
        if tank_collides_with_powerup(self.player, powerup):
          play_sound("pickup", 0.2)
          powerup.take(self.player)

      if powerup.done:
        play_sound("powerup", 0.2)
        self.powerups.remove(powerup)
        self.shields.add(Shield(self.player))
        for i in xrange(0, constants.POWERUP_PARTICLES):
          angle = i * 2 * math.pi / constants.POWERUP_PARTICLES
          d = Vector(angle)
          p = powerup.position
          c = powerup.colour_time
          particle = PowerupParticle(p, d, c)
          self.powerup_particles.add(particle)

    # add trail particles
    for particle in self.powerup_particles:
      while particle.trail_counter > constants.TRAIL_FREQUENCY:
        self.trail_particles.add(TrailParticle(particle.actual_position, particle.get_colour()))
        particle.trail_counter -= constants.TRAIL_FREQUENCY

    status = self.get_status()
    if not status == self.old_status and self.old_status == LEVEL_ONGOING:
      self.old_status = status
      if status == LEVEL_LOST:
        self.text = pygame.font.Font(None, 36).render("You lost... Press 'R' to restart", 1, (200, 200, 200))
        #self.timers.append(TimedLevelRestart(2000, self))
      if status == LEVEL_BEATEN:
        self.text = pygame.font.Font(None, 36).render("You won!", 1, (200, 200, 200))
        self.timers.append(TimedLevelAdvance(2000, self))

    to_remove = []
    for timer in self.timers:
      if timer.update(delta):
        to_remove.append(timer)
    for timer in to_remove:
      self.timers.remove(timer)

  def draw(self, screen):
    self.non_solid.draw(screen)
    self.tanks.draw(screen)
    self.turrets.draw(screen)
    self.enemies.draw(screen)
    self.enemy_turrets.draw(screen)
    self.shockwaves.draw(screen)
    self.explosions.draw(screen)
    self.solid.draw(screen)
    self.bullets.draw(screen)
    self.powerups.draw(screen)
    self.shields.draw(screen)
    self.powerup_particles.draw(screen)
    self.trail_particles.draw(screen)
    if self.text is not None:
      text_pos = self.text.get_rect(centerx = constants.RESOLUTION_X / 2)
      text_pos.top = 300
      screen.blit(self.text, text_pos)
