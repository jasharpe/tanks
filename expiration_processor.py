class ExpirationProcessor(object):
  def __init__(self, level):
    self.level = level

  def process(self):
    for expirables in self.level.config.expirable_groups:
      for expirable in list(expirables):
        if expirable.expired():
          expirables.remove(expirable)
          # Some expirables need to do something on expiration.
          # Let them do that here.
          if expirables in self.level.config.expirables_with_expire_actions:
            expirable.expire(self.level)
