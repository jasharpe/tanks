import sys, os
from main import Main
from editor.editor_game import EditorGame
import editor.editor_constants as editor_constants

class EditorMain(Main):
  def __init__(self):
    Main.__init__(self)

  def get_resolution(self):
    return [editor_constants.RESOLUTION_X, editor_constants.RESOLUTION_Y]

  def get_caption(self):
    return "Tanks! Editor"

  def get_game(self):
    return EditorGame()

  def usage(self):
    pass

  def handle_args(self, argv):
    pass

if __name__ == "__main__":
  os.environ['SDL_VIDEO_CENTERED'] = '1'
  sys.exit(EditorMain().main(sys.argv))
