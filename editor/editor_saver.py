import os
import constants

def save_level(editor, file_name):
  player = None
  enemies = []
  powerups = []
  for entity in editor.entities:
    if entity.name == "PLAYER":
      player = entity
    elif entity.name == "ENEMY":
      enemies.append(entity)
    elif entity.name in ["SPLASH", "REPAIR", "SHIELD"]:
      powerups.append(entity)
  
  lines = []
  with open(os.path.join(constants.DATA_DIR, file_name), "w") as f:
    lines.append("# level name")
    lines.append("A Temporary Level Name")
    lines.append("")
    lines.append("# board size")
    lines.append("(16, 16)")
    lines.append("")
    lines.append("# player start position and direction (in degrees)")
    lines.append("(%f, %f), %f" % (player.position.x, player.position.y, player.direction))
    lines.append("")
    lines.append("# ENEMIES, each given as")
    lines.append("# position, initial direction in degrees, waypoint type, list of waypoints")
    lines.append("START ENEMIES")
    for enemy in enemies:
      waypoints = ",".join(map(lambda x: "(%f, %f)" % (x.position.x, x.position.y), enemy.waypoints.waypoints))
      lines.append("(%f, %f), %f, LOOP, %s" % (enemy.position.x, enemy.position.y, enemy.direction, waypoints))
    lines.append("END ENEMIES")
    lines.append("")
    lines.append("START POWERUPS")
    for powerup in powerups:
      lines.append("%s, (%f, %f)" % (powerup.name, powerup.position.x, powerup.position.y))
    lines.append("END POWERUPS")
    lines.append("")
    lines.append("# tiles")
    lines.append("# W is a wall, G is ground")
    for x in xrange(0, constants.HORIZONTAL_TILES):
      tiles = []
      for y in xrange(0, constants.VERTICAL_TILES):
        tiles.append(editor.board.get_tile(x, y).type)
      lines.append("".join(tiles))
    f.write("\n".join(lines))
