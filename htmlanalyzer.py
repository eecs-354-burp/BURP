##
# Internal Functions for HTML Analysis
##

from pyquery import PyQuery
from lxml import etree
import urllib
import re

class HTMLAnalyzer:

  findJsExtension = re.compile('\.js[#?]?.*$')

  findHiddenStyle = re.compile('(?:display\s*:\s*none)|(?:visibility\s*:\s*hidden)')

  # These regular expressions match the values of the width and height
  # CSS rules when specified in "px" or without a unit
  findCssPropValue = {
    'width': re.compile('width\s*:\s*([\.\d-]+)(?:px)?\s*(?:;|$)'),
    'height': re.compile('height\s*:\s*([\.\d-]+)(?:px)?\s*(?:;|$)')
  }

  findNumber = re.compile('([\.\d-]+)')

  smallElementThreshold = 5;

  def __init__(self, html):
    self.load(html)

  ##
  # Loads an HTML string for analysis
  ##
  def load(self, html):
    self.html = html
    self.doc = PyQuery(html)

  ##
  # Returns a dictionary with the analysis results
  ##
  def analyze(self):
    return {
      'numChars': len( self.html ),
      'numWhitespaceChars': len( re.findall('\s', self.html) ),
      'numIframes': self.countElems('iframe'),
      'numScripts': self.countElems('script'),
      'numScriptsWithWrongExtension': self.countElems('script', self.hasWrongExtension),
      'numEmbeds': self.countElems('embed'),
      'numObjects': self.countElems('object'),
      'numHyperlinks': self.countElems('a'),
      'numMetaRefresh': self.countElems('meta', self.isRefresh),
      'numHiddenElements': self.countElems('*', self.isHidden),
      'numSmallElements': self.countElems('*', self.isSmall)
    }

  ##
  # Counts the number of elements matching the given tag name,
  # optionally filtered by a function
  ##
  def countElems(self, tagName, f = None):
    if f:
      return len( self.doc(tagName).filter(lambda i: f()) )
    else:
      return len( self.doc(tagName) )

  ##
  # Returns true if the PyQuery element (this)
  # has an "http-equiv" attribute with a value of "refresh"
  ##
  def isRefresh(self):
    httpEquiv = PyQuery(this).attr['http-equiv']
    return ( httpEquiv and httpEquiv.find('refresh') )

  ##
  # Returns true if the PyQuery element (this)
  # has a "src" attribute that points to a URI without a "js" extension
  ##
  def hasWrongExtension(self):
    src = PyQuery(this).attr['src'];
    return ( src and (self.findJsExtension.search(src) == None) );

  ##
  # Returns true if the PyQuery element (this)
  # has its CSS style set to "display: none" or "visibility: hidden"
  ##
  def isHidden(self):
    style = PyQuery(this).attr['style'];
    return ( style and (self.findHiddenStyle.search(style) != None) );

  ##
  # Returns the width or height of the given PyQuery element
  # (when set explicitly via the style, width, or height attributes)
  ##
  def getDimension(self, elem, dim):
    style = elem.attr['style']
    attr = elem.attr[dim]
    # Try to find the value of the CSS width and height properties first,
    # since they take precedence over the width and height HTML attributes
    match = ( (style and len(style) > 0 and self.findCssPropValue[dim].search(style)) or
              (attr and len(attr) > 0 and self.findNumber.search(attr)) or
              None )
    if match:
      value = match.group(1)
      # Cast to float or int appropriately
      return (float(value) if '.' in value else int(value))
    else:
      return None

  ##
  # Returns true if either the width or height of the PyQuery element (this)
  # are less than or equal to smallElementThreshold
  ##
  def isSmall(self):
    elem = PyQuery(this)
    width = self.getDimension(elem, 'width')
    height = self.getDimension(elem, 'height')
    return ( (width != None and (width <= self.smallElementThreshold)) or (height != None and (height <= self.smallElementThreshold)) )
