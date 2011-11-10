import pygame

DEFAULT_SETTINGS = {
    'music': True,
    'sound': True,
    'debug': False
}

# cheats
INFINITE_HEALTH = False

DATA_DIR = "data"
USER_DATA_DIR = "user_data"

TILE_SIZE = 50
HORIZONTAL_TILES = 16
VERTICAL_TILES = 16
RESOLUTION_X = TILE_SIZE * HORIZONTAL_TILES
RESOLUTION_Y = TILE_SIZE * VERTICAL_TILES
DEFAULT_TEXT_COLOR = pygame.Color(200, 200, 200)
SELECTED_TEXT_COLOR = pygame.Color(255, 200, 200)

DEBUG_LEVEL_LOAD_TIME = 200
LEVEL_LOAD_TIME = 2000

# the time in milliseconds before a screen responds to input
SCREEN_CHANGE_COOLDOWN = 1000

COLOR_TRANSPARENT = pygame.Color(0, 0, 0, 0)

TILE_WALL_COLOR = pygame.Color(150, 0, 0, 255)
TILE_GROUND_COLOR = pygame.Color(100, 100, 100, 255)

# Bullet
# speed in tiles per second
BULLET_SPEED = 5.0

BULLET_WIDTH_RATIO = 0.2
BULLET_HEIGHT_RATIO = 0.1
BULLET_COLOR = pygame.Color(20, 20, 150, 255)

# tank

# this is the number of seconds it takes to make one complete rotation
TANK_TURNING_SPEED = 9.0
TURRET_TURNING_SPEED = 3.0
# the acceleration, deceleration, and natural deceleration rate in
# tiles per second^2
ACCEL_SPEED = 0.6
DECEL_SPEED = 0.6
NEUTRAL_SPEED = 0.6
# max speed in tiles per second
MAX_SPEED = 1.2
# the size of the tank relative to a tile
TANK_SIZE_RATIO = 0.8
TURRET_LENGTH_RATIO = 0.6
TURRET_WIDTH_RATIO = 0.2
TANK_COLOR = pygame.Color(20, 150, 20, 255)
ENEMY_TANK_COLOR = pygame.Color(20, 150, 150, 255)
TANK_HEALTH = 3

SHOCKWAVE_DURATION = 600
SHOCKWAVE_MIN_RATIO = 0.2
SHOCKWAVE_MAX_RATIO = 0.5

BIG_EXPLOSION_MAX_RATIO = 1.0
BIG_EXPLOSION_MIN_RATIO = 0.2
EXPLOSION_MAX_RATIO = 0.5
EXPLOSION_MIN_RATIO = 0.1
EXPLOSION_DURATION = 200

TANK_MAX_BULLETS = 3
# number of milliseconds required between firings
TANK_COOLDOWN = 500
# the max range of a bullet in tiles before it explodes
BULLET_MAX_RANGE = 15.0

POWERUP_SIZE_RATIO = 0.6
POWERUP_COLOR_MODULATION_TIME = 1000
POWERUP_COLOR_ONE = pygame.Color(100, 0, 0, 255)
POWERUP_COLOR_TWO = pygame.Color(0, 0, 100, 255)
POWERUP_EXPLODE_TIME = 500
POWERUP_ACCEL = 5
POWERUP_PARTICLES = 8
POWERUP_PARTICLE_AMPLITUDE_RATIO = 0.1
POWERUP_PARTICLE_PERIOD_RATIO = 1.0
POWERUP_PARTICLE_AGE = 2000
POWERUP_PARTICLE_INIT_SPEED = 3
POWERUP_PARTICLE_DECEL = 1.5

TRAIL_PARTICLE_AGE = 500
TRAIL_FREQUENCY = 100

SHIELD_PULSE_PERIOD = 2000
SHIELD_RADIUS_RATIO = 0.6
SHIELD_COLOR = pygame.Color(0, 0, 100, 100)
SHIELD_COLOR_TWO = pygame.Color(0, 0, 200, 100)
SHIELD_GROWTH_TIME = 200
SHIELD_DEATH_TIME = 200
SHIELD_PULSE_COLOR = pygame.Color(100, 100, 100, 255)

SPLASH_TANK_DURATION = 10000
SPLASH_TANK_COLOR_PERIOD = 2000
SPLASH_TANK_COLOR = pygame.Color(60, 110, 20)
