class UpdateProcessor():
  def __init__(self, level):
    self.level = level

    # these are updated IN ORDER
    self.updateable_groups = [
        # tanks must be before turrets!
        self.level.enemies,
        self.level.enemy_turrets,
        self.level.player_tanks,
        self.level.player_turrets,
        self.level.bullets,
        self.level.shockwaves,
        self.level.explosions,
        self.level.powerups,
        self.level.powerup_particles,
        self.level.trail_particles,
        self.level.shields,
    ]

  def process(self):
    for group in self.updateable_groups:
      group.update(self.delta)
