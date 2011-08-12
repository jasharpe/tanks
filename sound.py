import pygame, os, constants

sounds = {}

def play_music(name, volume=1.0):
  fullname = os.path.join(constants.DATA_DIR, name)
  pygame.mixer.music.load(fullname)
  pygame.mixer.music.set_volume(volume)
  pygame.mixer.music.play(-1)

def pause_music():
  if pygame.mixer.music.get_busy():
    pygame.mixer.music.pause()

def unpause_music():
  pygame.mixer.music.unpause()

def stop_music():
  pygame.mixer.music.stop()

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
