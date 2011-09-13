import pygame

def linear(val, max, min=0):
  return (val - min) / float(max - min)

def reverse_linear(t, max, min):
  return t * (max - min) + min

# returns a bidirectional linear interpolation. 
def linear_bi(val, max, min=0):
  t = linear(val, max, min)
  return 1 - 2 * abs(t - 0.5)

def ease(t, easing_function):
  return (1 - t) * easing_function(t) + t * (-easing_function(1 - t) + 1)

def quadratic(val, max, min=0):
  return ease(linear(val, max, min), lambda x: x ** 2)

def quadratic_bi(val, max, min=0):
  return ease(linear_bi(val, max, min), lambda x: x ** 2)

def interpolate_colors(t, c1, c2):
  return pygame.Color(
      max(0, min(255, int(round(c1.r * t + c2.r * (1 - t))))),
      max(0, min(255, int(round(c1.g * t + c2.g * (1 - t))))),
      max(0, min(255, int(round(c1.b * t + c2.b * (1 - t))))),
      max(0, min(255, int(round(c1.a * t + c2.a * (1 - t)))))
  )
