import pygame, constants, math, sys
from menu import MainMenu
from victory import VictoryScreen
from sound import SoundManager
from level_loader import load_level
import getopt
from font import FontManager
from settings import Settings

FRAME_MS = 16
MAX_SKIPPED_DRAWS = 5

STAGE_LEVEL = 1
STAGE_MENU = 2
STAGE_VICTORY = 3

class Game:
  def __init__(self, starting_level=None):
    self.settings = Settings(constants.DEFAULT_SETTINGS)
    self.font_manager = FontManager(self.settings)
    self.sound_manager = SoundManager(self.settings)
    self.sound_manager.trigger_music("movemovemove.ogg", 0.7)
    self.levels = []
    # this is dumb :P
    for i in xrange(1, 10000):
      try:
        level = load_level(i, self)
        self.levels.append(level.name)
      except:
        break
    if starting_level is not None:
      self.current_level = starting_level
      self.max_level = self.current_level
      self.stage = STAGE_LEVEL
      self.restart_level()
      self.menu = None
    else:
      self.current_level = 1
      self.max_level = self.current_level
      self.stage = STAGE_MENU
      self.level = None
      self.menu = MainMenu(self, None)
    self.menu_stack = []
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
      self.max_level = max(self.max_level, self.current_level)
    except:
      self.level = None
      self.victory = VictoryScreen(self)
      self.stage = STAGE_VICTORY

  def restart_level(self):
    self.level = load_level(self.current_level, self)

  def go_to_level(self, level):
    self.current_level = level
    self.restart_level()
    self.stage = STAGE_LEVEL

  def enter_menu(self, sub_menu=None):
    if sub_menu is None:
      self.menu = MainMenu(self, self.level)
      self.menu_stack = []
      self.stage = STAGE_MENU
    else:
      self.menu_stack.append(self.menu)
      self.menu = sub_menu

  def back_menu(self):
    self.menu = self.menu_stack.pop()

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
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
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

def usage():
  print '''-l for starting level (for debug purposes)'''

def main(argv):
  try:
    opts, args = getopt.getopt(argv[1:], "l:", ["level="])
  except getopt.GetoptError:
    usage()
    return 2

  starting_level = None
  for opt, arg in opts:
    if opt in ("-l", "--level"):
      starting_level = int(arg)

  pygame.mixer.pre_init(frequency=22050, size=-16, channels=16, buffer=512)
  pygame.init()
  screen = pygame.display.set_mode(
      [constants.RESOLUTION_X, constants.RESOLUTION_Y])
  pygame.display.set_caption('Tanks!')

  game = Game(starting_level)

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

      time = (current_time - last_current_time)
      if time > 1:
        if game.settings['debug']:
          print "Last frame took %d" % (time)
    
    last_current_time = current_time

  pygame.quit()
  return 0

if __name__ == "__main__":
  sys.exit(main(sys.argv))
