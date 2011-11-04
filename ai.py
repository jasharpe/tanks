import random, math
from geometry import Vector, Point, Line

TIME_BETWEEN_FIRING = 3000

class TurretAI:
  def __init__(self, turret, level):
    self.turret = turret
    self.level = level

    self.cooldown = TIME_BETWEEN_FIRING

  def expired(self):
    return not self.turret in self.level.enemy_turrets

  def control(self, delta):
    # TODO: make the turret not fire if the bullet is going to rebound
    # right back into the tank!

    # the turret want to always be pointing at the player
    if not self.level.player.dead:
      self.turret.turn(delta, self.level.player.position)

      if self.cooldown == 0:
        self.cooldown = (random.random() + 0.5) * TIME_BETWEEN_FIRING
        return { 'turret' : self.turret }
      else:
        self.cooldown -= delta
        self.cooldown = max(0, self.cooldown)
    else:
      self.turret.turn_direction(delta, self.turret.tank.direction)

class TankAI:
  def __init__(self, tank, level, waypoints, waypoint_type):
    self.tank = tank
    self.level = level
    self.waypoints = waypoints
    self.waypoint_type = waypoint_type

    self.next_waypoint = 0
    
  def expired(self):
    return not self.tank in self.level.enemies

  def update_waypoint(self):
    if (self.tank.position - self.waypoints[self.next_waypoint]).length() < 0.01:
      self.next_waypoint = (self.next_waypoint + 1) % len(self.waypoints)

  def turn_towards(self, delta, point):
    # target angle
    t_a = (point - self.tank.position).angle()
    # current angle
    c_a = self.tank.direction
    difference = t_a - c_a
    while difference < -math.pi:
      difference += 2 * math.pi
    while difference > math.pi:
      difference -= 2 * math.pi

    if difference > 0:
      # turn right
      self.tank.turn_right(delta)
    elif difference < 0:
      # turn left
      self.tank.turn_left(delta)

  def control(self, delta):
    # if we're at the next waypoint, then change next waypoint
    self.update_waypoint()

    # point towards next waypoint
    self.turn_towards(delta, self.waypoints[self.next_waypoint])

    # if it gets us closer, accelerate
    desired = self.waypoints[self.next_waypoint] - self.tank.position
    actual = Vector(math.cos(self.tank.direction), math.sin(self.tank.direction))
    if desired.dot(actual) > 0:
      self.tank.accelerate(delta)
    elif desired.dot(actual) < 0:
      self.tank.decelerate(delta)
    else:
      self.tank.neutral(delta)
