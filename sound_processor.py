class SoundProcessor(object):
  def __init__(self, level):
    self.level = level

  def process(self):
    for group in self.level.config.sound_groups:
      for item in group:
        (sound, volume) = item.sound()
        if sound is not None:
          self.level.play_sound(sound, volume)
