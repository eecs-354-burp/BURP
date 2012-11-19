##
# *BURP* HTML Analyzer
##

import os
import sys
from pyquery import PyQuery as pq
from lxml import etree
import urllib

if not len(sys.argv) == 2:
  print("Usage: " + sys.argv[0] + " [URL]")
  exit(1)

url = sys.argv[1]

try:
  doc = pq(url)
except urllib.request.URLError:
  print("Error: Invalid URL")
  exit(1)

print("Success!")

