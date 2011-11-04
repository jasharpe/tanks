import pygame, constants
from geometry import *

class PlayerController(object):
  def __init__(self, tank, turret):
    self.tank = tank
    self.turret = turret

  # TODO: REMOVE delta from this call. Instead should register e.g. intent to
  # turn left with the object, then this should be evaluated elsewhere with
  # the delta.
  def control(self, events, pressed, mouse, delta):
    bullet_request = None
    for event in events:
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        bullet_request = { 'turret' : self.turret }

    if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
      self.tank.turn_left(delta)
    elif pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
      self.tank.turn_right(delta)
    if pressed[pygame.K_UP] or pressed[pygame.K_w]:
      self.tank.accelerate(delta)
    elif pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
      self.tank.decelerate(delta)
    else:
      self.tank.neutral(delta)

    # turret control
    # This is not quite accurate, as in cases where the tank hits a wall,
    # this will anticipate the tank's movement which has not actually
    # occurred. Probably not a real issue.
    self.turret.turn(delta, Point(float(mouse[0]) / constants.TILE_SIZE, float(mouse[1]) / constants.TILE_SIZE))

    return bullet_request
