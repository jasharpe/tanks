import pygame
import constants, math
from tank import Tank, Turret
from geometry import Vector, Point, Line, ORIGIN
from tile import Tile, TILE_RIGHT, TILE_LEFT, TILE_BOTTOM, TILE_TOP
from bullet import BOUNCED, EXPLODED
from explosion import Shockwave, Explosion
from level import Level
from menu import Menu
from victory import VictoryScreen
from sound import *
from level_loader import load_level

FRAME_MS = 16
MAX_SKIPPED_DRAWS = 5

STAGE_LEVEL = 1
STAGE_MENU = 2
STAGE_VICTORY = 3

class Game:
  def __init__(self):
    play_music("movemovemove.ogg", 0.7)
    self.stage = STAGE_MENU
    self.current_level = 1
    self.level = None
    self.menu = Menu(self, None)
    self.events = []
    self.should_quit = False
    self.victory = None

  # register an action to be executed before the next
  # update cycle. Do this in order to prevent changing
  # things in the middle of an update cycle which is Bad.
  def register_event(self, event):
    event.set_game(self)
    self.events.append(event)

  def resume(self):
    self.stage = STAGE_LEVEL

  def start_new_game(self):
    self.current_level = 1
    self.restart_level()
    self.stage = STAGE_LEVEL

  def quit(self):
    self.should_quit = True

  def advance_level(self):
    self.current_level += 1
    try:
      self.restart_level()
    except:
      self.level = None
      self.victory = VictoryScreen()
      self.stage = STAGE_VICTORY

  def restart_level(self):
    self.level = load_level(self.current_level, self)

  def enter_menu(self):
    self.menu = Menu(self, self.level)
    self.stage = STAGE_MENU

  def update(self, delta, pygame_events, pressed, mouse):
    old_stage = self.stage

    for event in self.events:
      event.do()
    self.events = []

    if self.should_quit:
      return True

    for event in pygame_events:
      if self.stage is STAGE_LEVEL:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
          self.level = load_level(self.current_level, self)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          self.enter_menu()
      elif self.stage is STAGE_VICTORY:
        if event.type == pygame.KEYDOWN:
          if self.victory.cooldown == 0:
            self.enter_menu()

    # do this check so we don't accidentally update with
    # unintentional input.
    # this kind of sucks, maybe there's a purpose to
    # update_controls() methods after all?
    if old_stage is self.stage:
      if self.stage is STAGE_LEVEL:
        self.level.update(delta, pygame_events, pressed, mouse)
      elif self.stage is STAGE_MENU:
        self.menu.update(delta, pygame_events, pressed, mouse)
      elif self.stage is STAGE_VICTORY:
        self.victory.update(delta, pygame_events, pressed, mouse)

    return False

  def draw(self, screen):
    if self.stage is STAGE_LEVEL:
      self.level.draw(screen)
    elif self.stage is STAGE_MENU:
      self.menu.draw(screen)
    elif self.stage is STAGE_VICTORY:
      self.victory.draw(screen)

def main():
  pygame.mixer.pre_init(frequency=22050, size=-16, channels=16, buffer=512)
  pygame.init()
  screen = pygame.display.set_mode(
      [constants.RESOLUTION_X, constants.RESOLUTION_Y])
  pygame.display.set_caption('Tanks!')

  game = Game()

  last_update_time = pygame.time.get_ticks()
  last_current_time = last_update_time
  exit_program = False
  while True:
    current_time = pygame.time.get_ticks()
    if current_time - last_update_time >= FRAME_MS:
      delta = FRAME_MS

      # event handling
      events = pygame.event.get()
      for event in events:
        if event.type == pygame.QUIT:
          exit_program = True

      if exit_program:
        break
    
      pressed = pygame.key.get_pressed()
      mouse = pygame.mouse.get_pos()

      if game.update(delta, events, pressed, mouse):
        break

      last_update_time += FRAME_MS

      # draw
      screen.fill((0, 0, 0))
      game.draw(screen) 
      pygame.display.flip()

      #time = (current_time - last_current_time)
      #if time > 1:
        #print "Last frame took %d" % (time)
    
    last_current_time = current_time


  pygame.quit()

if __name__ == "__main__":
  main()
