class ExpirationProcessor(object):
  def __init__(self, level):
    self.level = level

    # these are updated IN ORDER 
    self.expirable_groups = [
        self.level.powerup_particles,
        self.level.trail_particles,
        self.level.shields,
        self.level.shockwaves,
        self.level.explosions,
        self.level.enemy_ai,
        self.level.enemy_turret_ai,
        self.level.player_tanks,
        self.level.player_turrets,
        self.level.powerups,
    ]

    # order shouldn't matter here
    self.expirables_with_expire_actions = [
        self.level.shields,
        self.level.powerups,
    ]

  def process(self):
    for expirables in self.expirable_groups:
      for expirable in list(expirables):
        if expirable.expired():
          expirables.remove(expirable)
          # Some expirables need to do something on expiration.
          # Let them do that here.
          if expirables in self.expirables_with_expire_actions:
            expirable.expire(self.level)
