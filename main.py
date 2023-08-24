import pygame
#import reloader.reloader as reloader
#reloader.enable(ignore_existing_dependencies=True)
import sys, getopt, constants
from game import Game

FRAME_MS = 11

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
    screen = pygame.display.set_mode(self.get_resolution())
    
    self.set_caption(self.get_caption())

    game = self.get_game()

    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    frames = 0
    bad_frames = 0
    exit_program = False
    while True:
      clock.tick(91)

      frame_start_time = pygame.time.get_ticks()
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

      frame_end_time = pygame.time.get_ticks()
      frame_time = (frame_end_time - frame_start_time)
      if frame_time > FRAME_MS:
        if game.settings['debug']:
          bad_frames += 1
          print("Last frame took %d" % (frame_time))
      
      frames += 1

    total_time = (pygame.time.get_ticks() - start_time)
    #print "time per frame: %d" % (total_time / frames)
    #print "percent bad frames: %f%%" % (100 * float(bad_frames) / frames) 
    pygame.quit()
    return 0

class GameMain(Main):
  def __init__(self):
    Main.__init__(self)
    self.starting_level = None

  def get_resolution(self):
    return [constants.RESOLUTION_X, constants.RESOLUTION_Y]

  def get_caption(self):
    return "Tanks!"

  def get_game(self):
    return Game(self.starting_level)

  def usage(self):
    print('''-l for starting level (for debug purposes)''')

  def handle_args(self, argv):
    try:
      opts, args = getopt.getopt(argv[1:], "l:", ["level="])
    except getopt.GetoptError:
      usage()
      raise Exception("Failed to parse arguments")

    for opt, arg in opts:
      if opt in ("-l", "--level"):
        self.starting_level = int(arg)

def main(argv):
  return GameMain().main(argv)

if __name__ == "__main__":
  sys.exit(main(sys.argv))
