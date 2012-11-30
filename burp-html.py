##
# *BURP* HTML Analyzer
##

import os
import sys
import json
from htmlanalyzer import *

try:
  from urllib.request import URLError
except ImportError:
  from urllib2 import URLError

if not len(sys.argv) == 2:
  print("Usage: " + sys.argv[0] + " [URL]")
  exit(1)

url = sys.argv[1]

try:
  analysis = HTMLAnalyzer(url).analyze()
except URLError:
  print("Error: Invalid URL")
  exit(1)

print( json.dumps(analysis) )
