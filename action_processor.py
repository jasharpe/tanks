class ActionPostProcessor(object):
  def __init__(self, level, action_processor):
    self.level = level
    self.action_processor = action_processor

  def bullet_fire(self, bullet):
    self.level.play_sound("fire")
    self.level.bullets.add(bullet)
    self.level.stats.bullet_fired(bullet)

  def process(self):
    for bullet_request in self.action_processor.bullet_requests:
      bullet = bullet_request['turret'].fire()
      if bullet is not None:
        self.bullet_fire(bullet)

class ActionProcessor(object):
  def __init__(self, level):
    self.level = level

  def process(self):
    bullet_requests = self.process_input()
    bullet_requests += self.process_ai()
    self.bullet_requests = bullet_requests

  def process_input(self):
    bullet_requests = []

    for player_controller in self.level.player_controllers:
      bullet_request = player_controller.control(self.events, self.pressed, self.mouse, self.delta)
      if bullet_request is not None:
        bullet_requests.append(bullet_request)

    return bullet_requests

  def process_ai(self):
    bullet_requests = []

    # AI control of enemy tanks
    for enemy_ai in self.level.enemy_ai:
      enemy_ai.control(self.delta)

    # turret AI
    for turret_ai in self.level.enemy_turret_ai:
      bullet_request = turret_ai.control(self.delta)
      if bullet_request is not None:
        bullet_requests.append(bullet_request)

    return bullet_requests
