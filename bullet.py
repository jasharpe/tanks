import pygame, math
import constants
from geometry import Vector, Point, Line
from explosion import BigExplosion, Explosion, Shockwave

BOUNCED = 1
EXPLODED = 2

class Bullet(pygame.sprite.Sprite):
  # position holds xy coordinates of the bullet as a Point
  # direction contains an angle in radians from the positive
  # x axis.
  def __init__(self, p, direction, owner, splash=False):
    super(Bullet, self).__init__()
    
    self.position = p
    self.direction = direction
    self.owner = owner
    self.splash = splash

    if not self.splash:
      self.original = pygame.Surface([constants.TILE_SIZE * constants.BULLET_WIDTH_RATIO, constants.TILE_SIZE * constants.BULLET_HEIGHT_RATIO], flags=pygame.SRCALPHA)
      self.original.fill(constants.BULLET_COLOR)
    else:
      size = int(round(constants.BULLET_WIDTH_RATIO * constants.TILE_SIZE))
      self.original = pygame.Surface([size, size], flags=pygame.SRCALPHA)
      self.original.fill(constants.COLOR_TRANSPARENT)
      image_center = (self.original.get_width() / 2, self.original.get_height() / 2)
      pygame.draw.circle(self.original, constants.BULLET_COLOR, image_center, int(round(self.original.get_width() / 2)))
      
    self.old_position = self.position
    self.reset_vec()
    self.bounces = 0

    self.total_distance = 0.0
    self.dead = False

    self.travelled = Line(self.position, self.position)
    self.update_graphics()

  def get_explosion(self):
    if self.splash:
      return BigExplosion(self.position, True)
    else:
      return Explosion(self.position)

  def die(self):
    self.owner.bullets -= 1
    self.dead = True

  def has_bounces(self):
    return self.bounces < 1

  def has_bounced(self):
    return self.bounces > 0

  def reset_vec(self):
    self.vec = Vector(math.cos(self.direction), math.sin(self.direction)).normalize()

  # bounce off wall (which is a line segment).
  # traces movement of bullet backwards 
  def bounce(self, tiles):
    results = []
    while True:
      if self.travelled.as_vector().length2() == 0:
        return results

      max_dist2 = -1.0
      reflectors = []
      for tile in tiles:
        # if the distance between the bullet and the center of the tile is
        # greater than the distance travelled by the bullet plus the
        # size of the tile, then no collision could have occurred
        if self.travelled.length() + math.sqrt(2) / 2 < (self.position - tile.position).length():
          continue
        
        for tile_side in tile.get_sides():
          # first check that we're coming from the right direction
          if self.travelled.as_vector().normalize().dot(tile_side.normal()) > 0:
            continue
          p = self.travelled.intersect_segments(tile_side)
          if not p is None:
            if reflectors is None or (p - self.position).length2() > max_dist2:
              reflectors = [(p, tile_side)]
            elif max_dist2 < (p - self.position).length2() <= max_dist2:
              reflectors.append((p, tile_side))
      
      if len(reflectors) == 1:
        if self.has_bounces() and not self.splash:
          (p, wall) = reflectors[0]
          self.position = wall.reflect(self.position)
          self.direction = (self.position - p).angle()
          self.travelled = Line(p, self.position)
          self.reset_vec()
          self.bounces += 1

          self.update_graphics()

          results.append((BOUNCED, self.position))
        else:
          results.append((EXPLODED, self.position))
          break
      elif reflectors:
        print "multiple reflectors!"
      else:
        break
    return results

  def update(self, delta):
    self.old_position = self.position
    displacement = (constants.BULLET_SPEED * delta / 1000.0) * self.vec
    self.total_distance += displacement.length()
    self.position = self.position.translate(displacement)
    self.travelled = Line(self.old_position, self.position)
    self.update_graphics()

  def update_graphics(self):
    self.image = pygame.transform.rotate(self.original, -self.direction * 180.0 / math.pi)
    self.rect = self.image.get_rect(center=(constants.TILE_SIZE * self.position.x, constants.TILE_SIZE * self.position.y))
