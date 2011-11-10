import constants
import collision_detection as cd
from bullet import BOUNCED, EXPLODED
from explosion import Shockwave, BigExplosion
from tank import TANK_EXPLODED

class CollisionProcessor(object):
  def __init__(self, level):
    self.level = level

  def process(self):
    self.resolve_tanks()
    self.resolve_bullets()
    self.resolve_explosions()
    self.resolve_powerups()

  def resolve_powerups(self):
    for powerup in self.level.powerups:
      for player in self.level.player_tanks:
        if not powerup.taken:
          if powerup.can_take(player) and cd.sprite_collide(player, powerup):
            self.level.play_sound("pickup", 0.2)
            powerup.take(player)
            player.taking.add(powerup)

  def resolve_explosions(self):
    for explosion in self.level.explosions:
      for tank in self.level.all_tanks():
        if explosion.damages and not tank in explosion.damaged and cd.sprite_collide(tank, explosion):
          #self.level.stats.bullet_hit(explosion.bullet, tank)
          if self.tank_damage(tank):
            self.level.play_sound("tank_explode")
            # TODO, add a bullet origin to explosions so they can be
            # credited to the correct player.
            #self.level.stats.kill(explosion.bullet, tank)
          explosion.damaged.add(tank)

  def tank_explode(self, tank):
    self.level.explosions.add(BigExplosion(tank.position))
    tank.kill()
    tank.turret.kill()

  def tank_damage(self, tank):
    if tank.hurt() is TANK_EXPLODED:
      self.tank_explode(tank)
      return True
    return False

  def bullet_explode(self, bullet):
    self.level.explosions.add(bullet.get_explosion())
    bullet.remove(self.level.bullets)
    bullet.die()

  def resolve_bullets(self):
    resolvers = [
      self.resolve_shields_and_bullet,
      self.resolve_tanks_and_bullet,
      self.resolve_bullets_and_bullet,
      self.resolve_distance_and_bullet,
      self.resolve_walls_and_bullet
    ]

    for bullet in self.level.bullets:
      for resolver in resolvers:
        if bullet.dead: continue
        resolver(bullet)

  def resolve_walls_and_bullet(self, bullet):
    results = bullet.bounce(self.level.solid)
    for (result, position) in results:
      if result == EXPLODED:
        self.level.play_sound("bullet_explode")
        self.bullet_explode(bullet)
      elif result == BOUNCED:
        self.level.play_sound("pong", 0.35)
        self.level.shockwaves.add(Shockwave(position))

  def resolve_distance_and_bullet(self, bullet):
    if bullet.total_distance > constants.BULLET_MAX_RANGE:
      self.level.play_sound("bullet_explode")
      self.bullet_explode(bullet)

  def resolve_bullets_and_bullet(self, bullet):
    for bullet2 in filter(lambda x: x is not bullet, self.level.bullets):
      if cd.bullet_collides_with_bullet(bullet, bullet2):
        self.level.play_sound("bullet_explode")
        self.bullet_explode(bullet)
        self.bullet_explode(bullet2)

        self.level.stats.bullet_collision(bullet, bullet2)

  def resolve_shields_and_bullet(self, bullet):
    for shield in self.level.shields:
      if shield.active and cd.bullet_collides_with_shield(bullet, shield):
        # destroy the shield
        self.level.play_sound("shield_die")
        shield.die()
        
        # explode the bullet
        self.level.play_sound("bullet_explode")
        self.bullet_explode(bullet)

        self.level.stats.bullet_hit(bullet, shield.tank)

  def resolve_tanks_and_bullet(self, bullet):
    for tank in self.level.all_tanks():
      if not tank.dead and cd.bullet_collides_with_tank(bullet, tank): 
        # do something to the player
        self.level.stats.bullet_hit(bullet, tank)
        if self.tank_damage(tank):
          self.level.play_sound("tank_explode")
          self.level.stats.kill(bullet, tank)
        else:
          self.level.play_sound("bullet_explode")

        # explode the bullet
        self.bullet_explode(bullet)

  def resolve_tanks(self):
    for tank in self.level.all_tanks():
      if cd.tank_collides_with_tile(tank, self.level.solid):
        tank.revert()

    # check for tank to tank collisions
    conflicts = True
    loops = 0
    while conflicts:
      loops += 1
      # break out if we've obviously hit an infinite loop
      if loops > 20:
        if self.level.game.settings['debug']:
          print "tank collision resolution hit an infinite loop"
        break
      conflicts = False
      for tank1 in self.level.all_tanks():
        for tank2 in self.level.all_tanks():
          if tank1 is not tank2 and not tank1.dead and not tank2.dead and cd.tank_collides_with_tank(tank1, tank2):
            conflicts = True

            def revert(t1, t2):
              t1.revert()
              if cd.tank_collides_with_tank(t1, t2):
                t2.revert()

            # revert the enemy first, if there is one
            if tank2 in self.level.enemies:
              revert(tank2, tank1)
            else:
              revert(tank1, tank2)
