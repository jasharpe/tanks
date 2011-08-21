import pygame, sys, getopt, constants
from game import Game

FRAME_MS = 16
MAX_SKIPPED_DRAWS = 5

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

if __name__ == "__main__":
  sys.exit(main(sys.argv))
