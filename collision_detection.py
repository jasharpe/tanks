import pygame, constants

def tank_collides_with_tank(tank1, tank2):
    if not pygame.sprite.collide_rect(tank1, tank2):
      return False

    tank1_sides = tank1.get_sides()
    tank2_sides = tank2.get_sides()
    for tank1_side in tank1_sides:
      for tank2_side in tank2_sides:
        p = tank1_side.intersect_segments(tank2_side)
        if p is not None:
          return True
    
    return False

def bullet_collides_with_bullet(bullet1, bullet2):
  return pygame.sprite.collide_rect(bullet1, bullet2)

def bullet_collides_with_shield(bullet, shield):
  if bullet.owner is shield.tank and bullet.total_distance < constants.SHIELD_RADIUS_RATIO and not bullet.has_bounced():
    return False
  return sprite_collide(bullet, shield)

def bullet_collides_with_tank(bullet, tank):
  # if this is the owner and we haven't yet travelled past the
  # end of the tank, this can't be a hit!
  if tank is bullet.owner and bullet.total_distance < constants.TANK_SIZE_RATIO / 2 and not bullet.has_bounced():
    return False

  pos = bullet.position.scale(constants.TILE_SIZE)

  # if the bullet is not in the tank's rect, then a collision
  # could not have occurred.    
  if not tank.rect.collidepoint(pos):
    return False

  # now check the pixel of the tank's image where the bullet is.
  # if it's not transparent it's a collision.
  pixel = (
      max(0, min(tank.rect.width - 1, int(round(pos[0] - tank.rect.x)))),
      max(0, min(tank.rect.height - 1, int(round(pos[1] - tank.rect.y))))
  )
  color = tank.image.get_at(pixel)
  return color[3] != 0

def tank_collides_with_tile(tank, tiles):
  for tile in tiles:
    # if the rects don't even collide, then they don't collide
    if not pygame.sprite.collide_rect(tank, tile):
      continue
    
    # otherwise, have to verify collision in case of turned tank
    intersects = []
    for side in tank.get_sides():
      for tile_side in tile.get_sides():
        p = side.intersect_segments(tile_side)
        if not p is None:
          intersects.append((side, tile_side, p))

    if intersects:
      return intersects

  return []

def is_transparent(color):
  return color[3] == 0

def sprite_collide_exact(sprite1, sprite2):
  x_offset = sprite1.rect.x - sprite2.rect.x
  y_offset = sprite1.rect.y - sprite2.rect.y
  
  for x in xrange(0, sprite1.image.get_width()):
    sprite2_x = x + x_offset
    if sprite2_x < 0 or sprite2_x >= sprite2.image.get_width():
      continue
    for y in xrange(0, sprite1.image.get_height()):
      sprite2_y = y + y_offset
      if sprite2_y < 0 or sprite2_y >= sprite2.image.get_height():
        continue

      if not is_transparent(sprite1.image.get_at((x, y))) and \
         not is_transparent(sprite2.image.get_at((sprite2_x, sprite2_y))):
        return True

  return False

def sprite_collide(sprite1, sprite2):
  return pygame.sprite.collide_rect(sprite1, sprite2) and \
         sprite_collide_exact(sprite1, sprite2)

def sprite_contains_exact(sprite, point):
  x_offset = int(round(point.x - sprite.rect.x))
  y_offset = int(round(point.y - sprite.rect.y))
  return not is_transparent(sprite.image.get_at((x_offset, y_offset)))

def sprite_contains(sprite, point):
  return sprite.rect.collidepoint(point) and \
         sprite_contains_exact(sprite, point)
