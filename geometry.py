import math, operator

class Vector:
  def __init__(self, x_or_a, y_or_none=None):
    if y_or_none is None:
      # treat x as an angle instead
      x = math.cos(x_or_a)
      y = math.sin(x_or_a)
      length = math.sqrt(x * x + y * y)
      self.x = x / length
      self.y = y / length
    else:
      self.x = x_or_a
      self.y = y_or_none

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

  def dot(self, v):
    return self.x * v.x + self.y * v.y

  def angle(self):
    return math.atan2(self.y, self.x)

  def normalize(self):
    length = self.length()
    if length == 0:
      raise Exception("Attempted to normalize zero vector")
      return Vector(0, 0)
    return Vector(self.x / length, self.y / length)

  def length(self):
    return math.sqrt(self.length2())

  def length2(self):
    return self.x * self.x + self.y * self.y

class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def __len__(self):
    return 2

  def __getitem__(self, key):
    if type(key) is int:
      if key == 0:
        return self.x
      elif key == 1:
        return self.y
      else:
        raise IndexError("key is not 0 or 1")
    raise TypeError("key is not int")

  def __repr__(self):
    return "Point(%f, %f)" % (self.x, self.y)

  def __sub__(self, p):
    return Vector(self.x - p.x, self.y - p.y)

  def translate(self, v):
    return Point(self.x + v.x, self.y + v.y)

  def scale(self, s):
    return Point(self.x * s, self.y * s)

  def int_round(self):
    return Point(int(round(self.x)), int(round(self.y)))

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

  def as_vector(self):
    return self.p2 - self.p1

  # Returns the length of the line segment
  def length(self):
    return (self.p2 - self.p1).length()

  # returns a normal to the line
  def normal(self):
    dx = self.p2.x - self.p1.x
    dy = self.p2.y - self.p1.y
    return Vector(dy, -dx).normalize()

  # returns the reflection of p across this line
  def reflect(self, p):
    A = -self.B
    B = self.A
    C = A * p.x + B * p.y
    # find second point on line
    if B != 0:
      x2 = p.x + 1.0
      y2 = (C - A * x2) / B
      p2 = Point(x2, y2)
    else:
      y2 = p.y + 1.0
      x2 = (C - B * y2) / A
      p2 = Point(x2, y2)
    perp = Line(p, p2)
    intersect = self.intersect(perp)
    return p.translate(2 * (intersect - p))

  def intersect(self, l):
    det = self.A * l.B - l.A * self.B
    if (det == 0):
      return None
    else:
      return Point((l.B * self.C - self.B * l.C) / det, (self.A * l.C - l.A * self.C) / det)

  # returns the point that is the intersection between
  # this line and the given line, or None if one doesn't exist
  # (if the lines are parallel, or the line segments don't
  # actually intersect).
  def intersect_segments(self, l):
    p = self.intersect(l)
    if p is None:
      return None

    if (min(self.p1.x, self.p2.x) <= p.x <= max(self.p1.x, self.p2.x) or self.p1.x == self.p2.x) and \
       (min(self.p1.y, self.p2.y) <= p.y <= max(self.p1.y, self.p2.y) or self.p1.y == self.p2.y) and \
       (min(l.p1.x, l.p2.x) <= p.x <= max(l.p1.x, l.p2.x) or l.p1.x == l.p2.x) and \
       (min(l.p1.y, l.p2.y) <= p.y <= max(l.p1.y, l.p2.y) or l.p1.y == l.p2.y):
      return p
    else:
      return None
