import random

TIME_BETWEEN_FIRING = 2000

class TurretAI:
  def __init__(self, turret, level):
    self.turret = turret
    self.level = level

    self.cooldown = TIME_BETWEEN_FIRING

  def control(self, delta):
    # the turret want to always be pointing at the player
    if not self.level.player.dead:
      self.turret.turn(delta, self.level.player.position)

      if self.cooldown == 0:
        self.cooldown = TIME_BETWEEN_FIRING
        return None
        #return self.turret.fire()
      else:
        self.cooldown -= delta
        self.cooldown = max(0, self.cooldown)
    else:
      self.turret.turn_direction(delta, self.turret.tank.direction)

class TankAI:
  def __init__(self, tank, level):
    self.tank = tank
    self.level = level

  def control(self, delta):
    pass
    #self.tank.accelerate(delta)
