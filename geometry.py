import math

class Vector:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def __repr__(self):
    return "Vector(%f, %f)" % (self.x, self.y)

  def __add__(self, v):
    return Vector(self.x + v.x, self.y + v.y)

  def __neg__(self):
    return Vector(-self.x, -self.y)

  def __sub__(self, v):
    return Vector(self.x - v.x, self.y - v.y)

  def __mul__(self, s):
    return Vector(self.x * s, self.y * s)

  def __rmul__(self, s):
    return Vector(self.x * s, self.y * s)

  def normalize(self):
    length = math.sqrt(self.x * self.x + self.y * self.y)
    if length == 0:
      print "Attempted to normalize zero vector"
      return Vector(0, 0)
    return Vector(self.x / length, self.y / length)  

class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def __repr__(self):
    return "Point(%.02f, %.02f)" % (self.x, self.y)

  def __sub__(self, p):
    return Vector(self.x - p.x, self.y - p.y)

  def translate(self, v):
    return Point(self.x + v.x, self.y + v.y)

  # returns this point, rotated a radians about the origin
  def rotate(self, a):
    return Point(
        self.x * math.cos(a) - self.y * math.sin(a),
        self.x * math.sin(a) + self.y * math.cos(a))

  # returns this point, rotated a radians about point p
  def rotate_about(self, a, p):
    return self.translate(ORIGIN - p).rotate(a).translate(p - ORIGIN)

ORIGIN = Point(0, 0)

class Line:
  def __init__(self, p1, p2):
    self.p1 = p1
    self.p2 = p2
    self.A = p2.y - p1.y
    self.B = p1.x - p2.x
    self.C = self.A * p1.x + self.B * p1.y

  def __repr__(self):
    return "Line(%s, %s)" % (self.p1, self.p2)

  # returns the point that is the intersection between
  # this line and the given line, or None if one doesn't exist
  # (if the lines are parallel, or the line segments don't
  # actually intersect).
  def intersect_segments(self, l):
    det = self.A * l.B - l.A * self.B
    if (det == 0):
      return None
    else:
      p = Point((l.B * self.C - self.B * l.C) / det, (self.A * l.C - l.A * self.C) / det)
      if min(self.p1.x, self.p2.x) <= p.x <= max(self.p1.x, self.p2.x) and \
         min(self.p1.y, self.p2.y) <= p.y <= max(self.p1.y, self.p2.y) and \
         min(l.p1.x, l.p2.x) <= p.x <= max(l.p1.x, l.p2.x) and \
         min(l.p1.y, l.p2.y) <= p.y <= max(l.p1.y, l.p2.y):
        return p
      else:
        return None
