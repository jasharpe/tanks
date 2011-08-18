import constants, os

class Settings:
  def __init__(self, default_settings):
    self.d = default_settings
    try:
      with open(os.path.join(constants.USER_DATA_DIR, "settings"), 'r') as f:
        for line in f.readlines():
          line = line.rstrip().split(":")
          (k, v) = line
          self.d[k] = v == 'True'
    except Exception as e:
      print e

  def write_settings(self):
    if not os.path.exists(constants.USER_DATA_DIR):
        os.makedirs(constants.USER_DATA_DIR)
    
    with open(os.path.join(constants.USER_DATA_DIR, "settings"), 'w') as f:
      for (k, v) in self.d.items():
        f.write("%s:%s\n" % (k, v))

  def __getitem__(self, k):
    return self.d[k]

  def __setitem__(self, k, v):
    self.d[k] = v
    self.write_settings()
