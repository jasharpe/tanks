import constants
import pygame

class CollisionCircle(pygame.sprite.Sprite):
  def __init__(self, target, diameter):
    pygame.sprite.Sprite.__init__(self)

    self.target = target
    self.diameter = diameter

  def update(self):
    size = int(round(constants.TILE_SIZE * self.diameter))
    self.image = pygame.Surface([size, size], flags=pygame.SRCALPHA)
    self.image.fill(constants.COLOR_TRANSPARENT)
    center = self.target.position.scale(constants.TILE_SIZE)
    image_center = (self.image.get_width() / 2, self.image.get_height() / 2)
    pygame.draw.circle(self.image, (0, 0, 0, 255), image_center, int(round(self.image.get_width() / 2)))
    self.rect = self.image.get_rect(center=center)
