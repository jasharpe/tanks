import pygame, sys, getopt, constants
from game import Game
from editor import EditorGame

FRAME_MS = 16

class Main(object):

  def set_caption(self, caption):
    pygame.display.set_caption(caption)

  def main(self, argv):
    try:
      self.handle_args(argv)
    except:
      return 2

    pygame.mixer.pre_init(frequency=22050, size=-16, channels=16, buffer=512)
    pygame.init()
    screen = pygame.display.set_mode(
        [constants.RESOLUTION_X, constants.RESOLUTION_Y])
    
    self.set_caption(self.get_caption())

    game = self.get_game()

    last_current_time = pygame.time.get_ticks()
    clock = pygame.time.Clock()
    exit_program = False
    while True:
      clock.tick(60)

      current_time = pygame.time.get_ticks()
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

      # draw
      screen.fill((0, 0, 0))
      game.draw(screen) 
      pygame.display.flip()

      time = (current_time - last_current_time)
      if time > FRAME_MS:
        if game.settings['debug']:
          print "Last frame took %d" % (time)
      
      last_current_time = current_time

    pygame.quit()
    return 0

class GameMain(Main):
  def __init__(self):
    Main.__init__(self)
    self.starting_level = None

  def get_caption(self):
    return "Tanks!"

  def get_game(self):
    return Game(self.starting_level)

  def usage(self):
    print '''-l for starting level (for debug purposes)'''

  def handle_args(self, argv):
    try:
      opts, args = getopt.getopt(argv[1:], "l:", ["level="])
    except getopt.GetoptError:
      usage()
      raise Exception("Failed to parse arguments")

    for opt, arg in opts:
      if opt in ("-l", "--level"):
        self.starting_level = int(arg)

if __name__ == "__main__":
  sys.exit(GameMain().main(sys.argv))
