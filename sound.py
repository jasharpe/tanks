import pygame, os, constants

sounds = {}

def play_sound(name, volume=1.0):
  global sounds
  if not name in sounds:
    sounds[name] = load_sound(name)
  sounds[name].set_volume(volume)
  sounds[name].play()

def load_sound(name):
  class NoneSound:
    def play(self): pass
  if not pygame.mixer:
    return NoneSound()
  fullname = os.path.join(constants.DATA_DIR, name + ".wav")
  try:
    sound = pygame.mixer.Sound(fullname)
  except pygame.error, message:
    print "cannot load sound:", fullname
    raise SystemExit, message
  return sound
