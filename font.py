import pygame, constants, os

blacklist = set(['lucidacalligraphy', 'gulimgulimchedotumdotumche', 'lucidasanstypewriter', 'gillsansextcondensed','aharoni', 'britannic', 'andy', 'vivaldi', 'berlinsansfbdemi', 'twcencondensedextra', 'meiryomeiryoboldmeiryouiboldmeiryouibolditalic', 'lucidahandwriting', 'rockwellextra', 'gillsansultra', 'batangbatangchegungsuhgungsuhche', 'aparajitaitali', 'meiryomeiryomeiryouimeiryouiitalic', 'harlowsolid', 'arialrounded', 'script', 'utsaahitali', 'magneto', 'rage', 'kokilaitali', 'gillsansultracondensed', 'cambria', 'brushscript'])
font = 'stencil'

class FontManager:
  def __init__(self, settings):
    self.settings = settings
    self.fonts = pygame.font.get_fonts()
    self.font = 0
    while self.fonts[self.font] in blacklist:
      self.font = (self.font + 1) % len(self.fonts)
    self.next_font()

  def previous_font(self):
    self.font = (self.font - 1) % len(self.fonts)
    while self.fonts[self.font] in blacklist:
      self.font = (self.font - 1) % len(self.fonts)
    if self.settings['debug']:
      print self.fonts[self.font]

  def next_font(self):
    self.font = (self.font + 1) % len(self.fonts)
    while self.fonts[self.font] in blacklist:
      self.font = (self.font + 1) % len(self.fonts)
    if self.settings['debug']:
      print self.fonts[self.font]

  def get_numeral_font(self, size):
    return pygame.font.Font(os.path.join(constants.DATA_DIR, "Army.ttf"), 36)
    return pygame.font.SysFont(font, 36)
    return pygame.font.SysFont("arial", size)

  def get_font(self, size):
    return pygame.font.Font(os.path.join(constants.DATA_DIR, "Army.ttf"), 36)
    return pygame.font.SysFont(font, 36)
    #return pygame.font.SysFont(self.fonts[self.font], size)
