import constants
from particle import TrailParticle

class ParticleProcessor(object):
  def __init__(self, level):
    self.level = level

  def process(self):
    # add trail particles
    for particle in self.level.powerup_particles:
      while particle.trail_counter > constants.TRAIL_FREQUENCY:
        self.level.trail_particles.add(TrailParticle(particle.actual_position, particle.get_color()))
        particle.trail_counter -= constants.TRAIL_FREQUENCY
