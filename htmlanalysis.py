##
# Internal Functions for HTML Analysis
##

from pyquery import PyQuery as pq
from lxml import etree
import urllib

def loadDocument(src):
  try:
    return pq(src)
  except urllib.request.URLError:
    print("Error: Invalid URL")
    exit(1)

def countElements(doc, element):
  return len( doc(element) )

def countHiddenElements(doc):
  return len( doc("body *") )

