import sys
from main import Main
from editor import EditorGame

class EditorMain(Main):
  def __init__(self):
    Main.__init__(self)

  def get_caption(self):
    return "Tanks! Editor"

  def get_game(self):
    return EditorGame()

  def usage(self):
    pass

  def handle_args(self, argv):
    pass

if __name__ == "__main__":
  sys.exit(EditorMain().main(sys.argv))
