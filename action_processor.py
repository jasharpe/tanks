from mine import Mine

class ActionPostProcessor(object):
  def __init__(self, level, action_processor):
    self.level = level
    self.action_processor = action_processor

  def bullet_fire(self, bullet):
    self.level.play_sound("fire")
    self.level.bullets.add(bullet)
    self.level.stats.bullet_fired(bullet)

  def mine_lay(self, mine):
    self.level.mines.add(mine)

  def process(self):
    for bullet_request in self.action_processor.bullet_requests:
      bullet = bullet_request['turret'].fire()
      if bullet is not None:
        self.bullet_fire(bullet)

    for mine_request in self.action_processor.mine_requests:
      tank = mine_request['tank']
      if tank.can_lay_mine():
        self.mine_lay(Mine(tank.position, tank))
        tank.lay_mine()

class ActionProcessor(object):
  def __init__(self, level):
    self.level = level

  def process(self):
    (bullet_requests, mine_requests) = self.process_input()
    bullet_requests += self.process_ai()
    self.bullet_requests = bullet_requests
    self.mine_requests = mine_requests

  def process_input(self):
    bullet_requests = []
    mine_requests = []

    for player_controller in self.level.player_controllers:
      if not player_controller.tank.dead:
        (bullet_request, mine_request) = player_controller.control(self.events, self.pressed, self.mouse, self.delta)
        if bullet_request is not None:
          bullet_requests.append(bullet_request)

        if mine_request is not None:
          mine_requests.append(mine_request)

    return (bullet_requests, mine_requests)

  def process_ai(self):
    bullet_requests = []

    # AI control of enemy tanks
    for enemy_ai in self.level.enemy_ai:
      if not enemy_ai.tank.dead:
        enemy_ai.control(self.delta)

    # turret AI
    for turret_ai in self.level.enemy_turret_ai:
      if not turret_ai.turret.tank.dead:
        bullet_request = turret_ai.control(self.delta)
        if bullet_request is not None:
          bullet_requests.append(bullet_request)

    return bullet_requests
