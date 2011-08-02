import pygame

DATA_DIR = "data"

TILE_SIZE = 50
HORIZONTAL_TILES = 16
VERTICAL_TILES = 16
RESOLUTION_X = TILE_SIZE * HORIZONTAL_TILES
RESOLUTION_Y = TILE_SIZE * VERTICAL_TILES

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

SHOCKWAVE_DURATION = 600
SHOCKWAVE_MIN_RATIO = 0.2
SHOCKWAVE_MAX_RATIO = 0.5

EXPLOSION_MAX_RATIO = 0.5
EXPLOSION_MIN_RATIO = 0.1
EXPLOSION_DURATION = 200

TANK_MAX_BULLETS = 3
# number of milliseconds required between firings
TANK_COOLDOWN = 500
# the max range of a bullet in tiles before it explodes
BULLET_MAX_RANGE = 15.0
