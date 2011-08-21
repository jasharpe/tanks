class LevelStats:
  def __init__(self):
    self.bullets_fired = []
    self.bullet_hits = []
    self.bullet_collisions = []
    self.kills = []

  def bullet_fired(self, bullet):
    self.bullets_fired.append(bullet)

  def bullet_hit(self, bullet, hit_tank):
    self.bullet_hits.append((bullet, hit_tank))

  def bullet_collision(self, bullet1, bullet2):
    self.bullet_collisions.append((bullet1, bullet2))

  def kill(self, bullet, killed_tank):
    self.kills.append((bullet, killed_tank))

  def fired_shots(self, tank):
    return len(filter(
        lambda bullet: bullet.owner is tank,
        self.bullets_fired
    ))

  def hit_shots(self, tank):
    return len(filter(
        lambda (bullet, hit_tank): bullet.owner is tank and not hit_tank is tank,
        self.bullet_hits
    ))

  def blocked_shots(self, tank):
    blocked = 0
    for (bullet1, bullet2) in self.bullet_collisions:
      if bullet1.owner is tank:
        blocked += 1
      if bullet2.owner is tank:
        blocked += 1
    return blocked

  def accuracy(self, tank):
    total_fired = self.fired_shots(tank)
    total_hit = self.hit_shots(tank) + self.blocked_shots(tank)
    if total_fired == 0:
      return 1
    else:
      return total_hit / float(total_fired)

  def kill_total(self, tank):
    return len(filter(
        lambda (bullet, killed_tank): bullet.owner is tank and not tank is killed_tank,
        self.kills
    ))

  def friendly_fire_kills(self, tank):
    return len(filter(
        lambda (bullet, killed_tank): not bullet.owner is tank and not tank is killed_tank,
        self.kills
    ))
