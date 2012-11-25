##
# *BURP* HTML Analyzer
##

import os
import sys
import json
from htmlanalysis import *

if not len(sys.argv) == 2:
  print("Usage: " + sys.argv[0] + " [URL]")
  exit(1)

url = sys.argv[1]

try:
  f = urllib.urlopen(url)
  html = f.read()
except urllib.request.URLError:
  print("Error: Invalid URL")
  exit(1)

print( json.dumps( analyzeHtml(html) ) )
