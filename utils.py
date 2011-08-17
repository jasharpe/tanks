import random, pygame

def random_between(a, b):
  # between a and b
  return random.random() * (b - a) + a

def mult_colour(c, s):
  return pygame.Color(c.r * s, c.g * s, c.b * s, c.a)
