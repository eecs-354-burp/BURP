__all__ = ['url', 'html']

import os
import burp

def getWekaFile(filename):
  packageDir = burp.__path__[0]
  return os.path.join(packageDir, 'weka', filename)

