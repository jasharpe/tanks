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
import collision_detection as cd
from particle import *
from shield import Shield
from level_stats import LevelStats
from player import PlayerController
from collision_resolver import CollisionResolver
from action_processor import ActionProcessor

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

    self.collision_resolver = CollisionResolver(self)
    self.action_processor = ActionProcessor(self)

    self.player_start = player_start
    self.player_direction = player_direction
    self.board = board

    self.powerups = Group(powerups)

    self.shields = Group()

    self.powerup_particles = Group()
    self.trail_particles = Group()

    self.player_tanks = Group()
    self.player_turrets = Group()

    self.player = Tank(self.player_start, self.player_direction)
    self.player_tanks.add(self.player)
    self.player_turret = Turret(self.player)
    self.player_turrets.add(self.player_turret)
    self.player_controllers = [PlayerController(self.player, self.player_turret)]

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

    if self.game.settings['debug']:
      self.load_time = constants.DEBUG_LEVEL_LOAD_TIME
    else:
      self.load_time = constants.LEVEL_LOAD_TIME
    self.victory = False
    self.cooldown = -1

    self.paused = False

    # these are updated IN ORDER
    self.updateable_groups = [
        # tanks must be before turrets!
        self.enemies,
        self.enemy_turrets,
        self.player_tanks,
        self.player_turrets,
        self.bullets,
        self.shockwaves,
        self.explosions,
        self.powerups,
        self.powerup_particles,
        self.trail_particles,
        self.shields,
    ]

    # these are updated IN ORDER 
    self.expirable_groups = [
        self.powerup_particles,
        self.trail_particles,
        self.shields,
        self.shockwaves,
        self.explosions,
        self.enemy_ai,
        self.enemy_turret_ai,
        self.player_tanks,
        self.player_turrets,
        self.powerups,
    ]

    # order shouldn't matter here
    self.expirables_with_expire_actions = [
        self.shields,
        self.powerups,
    ]


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

  def update_timers(self, delta):
    for timer in list(self.timers):
      if timer.update(delta):
        self.timers.remove(timer)

  def check_for_status_change(self):
    status = self.get_status()
    if not status == self.old_status and self.old_status == LEVEL_ONGOING:
      self.old_status = status
      if status == LEVEL_LOST:
        self.text = self.game.font_manager.render("You lost... Press 'R' to restart", 40, constants.DEFAULT_TEXT_COLOR)
      if status == LEVEL_BEATEN:
        self.text = self.game.font_manager.render("Victory!", 40, constants.DEFAULT_TEXT_COLOR)
        self.timers.append(TimedLevelVictory(2000, self))

  def update_all(self, delta):
    for group in self.updateable_groups:
      group.update(delta)

  def process_particles(self):
    # add trail particles
    for particle in self.powerup_particles:
      while particle.trail_counter > constants.TRAIL_FREQUENCY:
        self.trail_particles.add(TrailParticle(particle.actual_position, particle.get_color()))
        particle.trail_counter -= constants.TRAIL_FREQUENCY

  def all_tanks(self):
    return itertools.chain(self.enemies, self.player_tanks)

  def expire_expirables(self):
    for expirables in self.expirable_groups:
      for expirable in list(expirables):
        if expirable.expired():
          expirables.remove(expirable)
          # Some expirables need to do something on expiration.
          # Let them do that here.
          if expirables in self.expirables_with_expire_actions:
            expirable.expire(self)

  def bullet_fire(self, bullet):
    self.play_sound("fire")
    self.bullets.add(bullet)
    self.stats.bullet_fired(bullet)

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

    self.action_processor.update_controls(events, pressed, mouse)

    self.action_processor.update_delta(delta)
    

    # make sure we don't have any expired things hanging around
    self.expire_expirables()
    # process all controls, both by the player, and by the AI
    # TODO: remove dependency on delta here
    self.action_processor.process()
    
    self.update_all(delta)
    # if any of the updates caused collisions, resolve these
    self.collision_resolver.resolve()
    self.expire_expirables()
    # actually fire bullets, since now final locations of turrets are known
    self.action_processor.complete_processing()
    self.process_particles()
    self.check_for_status_change()
    self.update_timers(delta)

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
    self.player_tanks.draw(screen)
    self.player_turrets.draw(screen)
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
