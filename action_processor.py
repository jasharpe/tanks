class ActionProcessor(object):
  def __init__(self, level):
    self.level = level

  def update_delta(self, delta):
    self.delta = delta

  def update_controls(self, events, pressed, mouse):
    self.events = events
    self.pressed = pressed
    self.mouse = mouse

  def process(self):
    bullet_requests = self.process_input()
    bullet_requests += self.process_ai()
    self.bullet_requests = bullet_requests

  def complete_processing(self):
    for bullet_request in self.bullet_requests:
      bullet = bullet_request['turret'].fire()
      if bullet is not None:
        self.level.bullet_fire(bullet)

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
