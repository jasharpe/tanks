import pygame
import constants, math
from tank import Tank, Turret
from geometry import Vector, Point, Line, ORIGIN
from tile import Tile, TILE_RIGHT, TILE_LEFT, TILE_BOTTOM, TILE_TOP
from bullet import BOUNCED, EXPLODED
from explosion import Shockwave, Explosion
from level import Level, load_level

FRAME_MS = 16
MAX_SKIPPED_DRAWS = 5

LEVEL = 1

def main():
  pygame.init()
  screen = pygame.display.set_mode(
      [constants.RESOLUTION_X, constants.RESOLUTION_Y])
  pygame.display.set_caption('Tanks!')

  stage = LEVEL

  level = load_level(1)

  #clock = pygame.time.Clock()
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
        elif stage == LEVEL:
          if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            level = load_level(1)

      if exit_program:
        break
     
      # control handling
      pressed = pygame.key.get_pressed()
      mouse = pygame.mouse.get_pos()
      if stage == LEVEL:
        level.update_controls(events, pressed, mouse)
        level.update(delta)
      
      last_update_time += FRAME_MS

      # draw

      screen.fill((0, 0, 0))
      
      if stage is LEVEL:
        level.draw(screen)

      pygame.display.flip()

      #time = (current_time - last_current_time)
      #if time > 1:
        #print "Last frame took %d" % (time)
    
    last_current_time = current_time


  pygame.quit()

if __name__ == "__main__":
  main()
