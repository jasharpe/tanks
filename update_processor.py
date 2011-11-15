class UpdateProcessor():
  def __init__(self, level):
    self.level = level

  def process(self):
    for group in self.level.config.updateable_groups:
      group.update(self.delta)
