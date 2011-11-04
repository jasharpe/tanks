import pygame, os, itertools
from pygame.sprite import Group
import constants
from ai import *
from board import Board
from tile import Tile, TILE_RIGHT, TILE_LEFT, TILE_BOTTOM, TILE_TOP
from geometry import Vector, Point, Line, ORIGIN
from tank import Tank, Turret, TANK_EXPLODED
from bullet import BOUNCED, EXPLODED
from explosion import Explosion, BigExplosion, Shockwave
from game_event import RestartLevelEvent, AdvanceLevelEvent, PlaySoundEvent
from powerup import ShieldPowerup, RepairPowerup, SplashPowerup
from collision import *
from particle import *
from shield import Shield
from level_stats import LevelStats

LEVEL_ONGOING = 1
LEVEL_BEATEN = 2
LEVEL_LOST = 3

LEVEL_INTRO = 1
LEVEL_OUTRO = 2
LEVEL_MAIN = 3

class TimedLevelAdvance:
  def __init__(self, time, level):
    self.level = level
    self.time_left = time

  def update(self, delta):
    self.time_left -= delta
    self.time_left = max(0, self.time_left)
    if self.time_left == 0:
      self.level.game.register_event(AdvanceLevelEvent(self.level))
    return self.time_left == 0

class TimedLevelVictory:
  def __init__(self, time, level):
    self.level = level
    self.time_left = time

  def update(self, delta):
    self.time_left -= delta
    self.time_left = max(0, self.time_left)
    if self.time_left == 0:
      self.level.victory = True
      self.level.cooldown = constants.SCREEN_CHANGE_COOLDOWN
    return self.time_left == 0

class TimedLevelRestart:
  def __init__(self, time, level):
    self.level = level
    self.time_left = time

  def update(self, delta):
    self.time_left -= delta
    self.time_left = max(0, self.time_left)
    if self.time_left == 0:
      self.level.game.register_event(RestartLevelEvent(self.level))
    return self.time_left == 0

class Level:
  def __init__(self, name, game, player_start, player_direction, board, enemies, powerups):
    self.stats = LevelStats()
    self.computed_stats = {}
    self.name = name
    self.game = game

    self.player_start = player_start
    self.player_direction = player_direction
    self.board = board

    self.powerups = Group(powerups)

    self.shields = Group()

    self.powerup_particles = Group()
    self.trail_particles = Group()

    self.tanks = Group()
    self.turrets = Group()

    self.player = Tank(self.player_start, self.player_direction)
    self.tanks.add(self.player)
    self.turret = Turret(self.player)
    self.turrets.add(self.turret)

    self.enemies = Group()
    self.enemy_turrets = Group()
    self.enemy_ai = []
    self.enemy_turret_ai = []
    for (p, d, waypoint_type, waypoints) in enemies:
      enemy = Tank(p, d, constants.ENEMY_TANK_COLOR)
      self.enemy_ai.append(TankAI(enemy, self, waypoints, waypoint_type))
      enemy_turret = Turret(enemy)
      self.enemies.add(enemy)
      self.enemy_turrets.add(enemy_turret)
      self.enemy_turret_ai.append(TurretAI(enemy_turret, self))

    self.tiles = Group()
    for tile in self.board:
      self.tiles.add(tile)
    self.solid = Group()
    self.non_solid = Group()
    for tile in self.tiles:
      if tile.solid:
        self.solid.add(tile)
      else:
        self.non_solid.add(tile)
    self.bullets = Group()
    self.shockwaves = Group()
    self.explosions = Group()
    self.old_status = LEVEL_ONGOING
    self.text = None

    self.timers = []

    self.load_time = constants.LEVEL_LOAD_TIME
    self.victory = False
    self.cooldown = -1

    self.paused = False
 
  def play_sound(self, name, volume=1.0):
    self.game.register_event(PlaySoundEvent(self, name, volume))

  def get_part(self):
    if self.load_time > 0:
      return LEVEL_INTRO
    if self.cooldown >= 0:
      return LEVEL_OUTRO
    return LEVEL_MAIN

  def get_status(self):
    if not self.enemies:
      return LEVEL_BEATEN
    if self.player.dead:
      return LEVEL_LOST
    return LEVEL_ONGOING

  def is_finished(self):
    return self.get_part() is LEVEL_OUTRO

  def bullet_explode(self, bullet):
    self.explosions.add(bullet.get_explosion())
    bullet.remove(self.bullets)
    bullet.die()

  def tank_explode(self, tank):
    self.explosions.add(BigExplosion(tank.position))
    tank.kill()
    tank.turret.kill()

  def tank_damage(self, tank):
    if tank.hurt() is TANK_EXPLODED:
      self.tank_explode(tank)
      return True
    return False

  def update(self, delta, events, pressed, mouse):
    self.load_time = max(0, self.load_time - delta)

    if self.load_time > 0:
      return

    if self.cooldown >= 0:
      self.cooldown = max(0, self.cooldown - delta)
    
    for event in events:
      if self.get_part() is LEVEL_OUTRO and (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN) and self.cooldown == 0:
        self.game.register_event(AdvanceLevelEvent(self))
      elif self.get_part() is LEVEL_MAIN and event.type == pygame.KEYDOWN and event.key == pygame.K_p:
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

      self.player.update(delta)
      if tank_collides_with_tile(self.player, self.solid):
        self.player.revert()

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
        self.play_sound("fire")
        self.bullets.add(bullet)
        self.stats.bullet_fired(bullet)

    # turret control
    # mouse position
    m_p = mouse
    if not self.player.dead:
      self.turret.turn(delta, Point(float(m_p[0]) / constants.TILE_SIZE, float(m_p[1]) / constants.TILE_SIZE))

      # fire!
      if fire:
        bullet = self.turret.fire()
        if not bullet is None:
          self.play_sound("fire")
          self.bullets.add(bullet)
          self.stats.bullet_fired(bullet)

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

    for shield in self.player.shields:
      if shield.to_remove:
        shield.remove(self.shields)
        self.player.shields.remove(shield)


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

      for shield in self.shields:
        if shield.active and bullet_collides_with_shield(bullet, shield):
          # destroy the shield
          self.play_sound("shield_die")
          shield.die()
          
          # explode the bullet
          self.play_sound("bullet_explode")
          self.bullet_explode(bullet)

          self.stats.bullet_hit(bullet, shield.tank)
      if bullet.dead: continue

      for tank in itertools.chain(self.enemies, [self.player]):
        if not tank.dead and bullet_collides_with_tank(bullet, tank): 
          # do something to the player
          self.stats.bullet_hit(bullet, tank)
          if self.tank_damage(tank):
            self.play_sound("tank_explode")
            self.stats.kill(bullet, tank)
          else:
            self.play_sound("bullet_explode")

          # explode the bullet
          self.bullet_explode(bullet)
      if bullet.dead: continue      

      # check for bullet/bullet collisions
      for bullet2 in filter(lambda x: x is not bullet, self.bullets):
        if bullet_collides_with_bullet(bullet, bullet2):
          self.play_sound("bullet_explode")
          self.bullet_explode(bullet)
          self.bullet_explode(bullet2)

          self.stats.bullet_collision(bullet, bullet2)
      if bullet.dead: continue

      # check for bullets reaching max range
      if bullet.total_distance > constants.BULLET_MAX_RANGE:
        self.play_sound("bullet_explode")
        self.bullet_explode(bullet)
      # check for bullet bounces or wall collisions
      else:
        results = bullet.bounce(self.solid)
        for (result, position) in results:
          if result == EXPLODED:
            self.play_sound("bullet_explode")
            self.bullet_explode(bullet)
          elif result == BOUNCED:
            self.play_sound("pong", 0.35)
            self.shockwaves.add(Shockwave(position))
      if bullet.dead: continue

    # check for collisions of splash explosions with tanks
    for explosion in self.explosions:
      for tank in itertools.chain(self.enemies, [self.player]):
        if explosion.damages and not tank in explosion.damaged and sprite_collide(tank, explosion):
          #self.stats.bullet_hit(explosion.bullet, tank)
          if self.tank_damage(tank):
            self.play_sound("tank_explode")
            # TODO, add a bullet origin to explosions so they can be
            # credited to the correct player.
            #self.stats.kill(explosion.bullet, tank)
          explosion.damaged.add(tank)

    # apply powerups
    for powerup in self.powerups:
      if not powerup.taken:
        if powerup.can_take(self.player) and sprite_collide(self.player, powerup):
          self.play_sound("pickup", 0.2)
          powerup.take(self.player)
          self.player.taking.add(powerup)

      if powerup.done:
        self.play_sound("powerup", 0.2)
        self.powerups.remove(powerup)

        powerup.do(self, self.player)
        self.player.taking.remove(powerup)
        for i in xrange(0, constants.POWERUP_PARTICLES):
          angle = i * 2 * math.pi / constants.POWERUP_PARTICLES
          d = Vector(angle)
          p = powerup.position
          c = powerup.color_time
          particle = PowerupParticle(p, d, c)
          self.powerup_particles.add(particle)

    # add trail particles
    for particle in self.powerup_particles:
      while particle.trail_counter > constants.TRAIL_FREQUENCY:
        self.trail_particles.add(TrailParticle(particle.actual_position, particle.get_color()))
        particle.trail_counter -= constants.TRAIL_FREQUENCY

    status = self.get_status()
    if not status == self.old_status and self.old_status == LEVEL_ONGOING:
      self.old_status = status
      if status == LEVEL_LOST:
        self.text = self.game.font_manager.render("You lost... Press 'R' to restart", 40, constants.DEFAULT_TEXT_COLOR)
      if status == LEVEL_BEATEN:
        self.text = self.game.font_manager.render("You won!", 40, constants.DEFAULT_TEXT_COLOR)
        self.timers.append(TimedLevelVictory(2000, self))

    to_remove = []
    for timer in self.timers:
      if timer.update(delta):
        to_remove.append(timer)
    for timer in to_remove:
      self.timers.remove(timer)

  def write_line(self, line, screen):
    text = self.game.font_manager.render(line, 50, constants.DEFAULT_TEXT_COLOR)
    text_pos = text.get_rect(centerx = constants.RESOLUTION_X / 2)
    text_pos.top = self.top
    self.top += text.get_height() + 10
    screen.blit(text, text_pos)

  def write_stat_line(self, part1, part2, screen):
    text = self.game.font_manager.render(part1, 40, constants.DEFAULT_TEXT_COLOR)
    text_pos = text.get_rect(right = constants.RESOLUTION_X / 2)
    text_pos.top = self.top
    screen.blit(text, text_pos)
    
    text = self.game.font_manager.render(part2, 40, constants.DEFAULT_TEXT_COLOR)
    text_pos = text.get_rect(left = 3 * constants.RESOLUTION_X / 4)
    text_pos.top = self.top
    screen.blit(text, text_pos)

    self.top += text.get_height() + 10

  def get_or_compute(self, stat, getter):
    if stat in self.computed_stats:
      value = self.computed_stats[stat]
    else:
      value = getter()
      self.computed_stats[stat] = value
    return value

  def draw(self, screen):
    if self.load_time > 0:
      self.top = 300
      self.write_line("%d. %s" % (self.game.current_level, self.name), screen)
      return

    if self.victory:
      # draw a stat screen
      self.top = 150
      self.write_line("Victory!", screen)
      self.top += 50
      fired_shots = self.get_or_compute("fired_shots", lambda: self.stats.fired_shots(self.player))
      self.write_stat_line("Fired Shots:", "%d" % fired_shots, screen)
      hit_shots = self.get_or_compute("hit_shots", lambda: self.stats.hit_shots(self.player))
      self.write_stat_line("Hits:", "%d" % hit_shots, screen)
      blocked_shots = self.get_or_compute("blocked_shots", lambda: self.stats.blocked_shots(self.player))
      self.write_stat_line("Blocked Shots:", "%d" % blocked_shots, screen)
      accuracy = self.get_or_compute("accuracy", lambda: self.stats.accuracy(self.player))
      accuracy_percentage = int(round(accuracy * 100))
      self.write_stat_line("Accuracy:", "%d%%" % accuracy_percentage, screen)
      kill_total = self.get_or_compute("kill_total", lambda: self.stats.kill_total(self.player))
      self.write_stat_line("Kills:", "%d" % kill_total, screen)
      friendly_fire_kills = self.get_or_compute("friendly_fire_kills", lambda: self.stats.friendly_fire_kills(self.player))
      self.write_stat_line("FF Kills:", "%d" % friendly_fire_kills, screen)
      if self.cooldown == 0:
        self.top += 50
        self.write_line("(Press any key to continue)", screen)
      return

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
