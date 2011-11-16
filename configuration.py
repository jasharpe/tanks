class Configuration(object):
  def __init__(self, level):
    self.level = level

  def configure(self):
    self.processors = [
        self.level.expiration_processor,
        # process all controls, both by the player, and by the AI
        self.level.action_processor,
        self.level.update_processor,
        self.level.collision_processor,
        self.level.expiration_processor,
        # actually fire bullets, since now final locations of turrets are known
        self.level.action_post_processor,
        self.level.particle_processor,
        self.level.sound_processor
    ]

    self.sound_groups = [
        self.level.mines,  
    ]

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
        self.level.mines,
    ]

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
        self.level.mines,
        self.level.bullets,
    ]

    # order shouldn't matter here
    self.expirables_with_expire_actions = [
        self.level.shields,
        self.level.powerups,
        self.level.mines,
    ]

    self.processors_with_delta = [
      self.level.action_processor,
      self.level.update_processor,
    ]

    self.drawables = [
        self.level.non_solid,
        self.level.mines,
        self.level.player_tanks,
        self.level.player_turrets,
        self.level.enemies,
        self.level.enemy_turrets,
        self.level.shockwaves,
        self.level.explosions,
        self.level.solid,
        self.level.bullets,
        self.level.powerups,
        self.level.shields,
        self.level.powerup_particles,
        self.level.trail_particles,
    ]
