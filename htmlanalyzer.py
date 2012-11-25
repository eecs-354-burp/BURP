##
# Internal Functions for HTML Analysis
##

from pyquery import PyQuery
from lxml import etree
import urllib
import re

class HTMLAnalyzer:

  findJsExtension = re.compile('\.js[#?]?.*$')

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
      'numIframes': self.countElems('iframe'),
      'numScripts': self.countElems('script'),
      'numScriptsWithWrongExtension': self.countElems('script', self.hasWrongExtension),
      'numEmbeds': self.countElems('embed'),
      'numObjects': self.countElems('object'),
      'numHyperlinks': self.countElems('a'),
      'numMetaRefresh': self.countElems('meta', self.isRefresh)
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
  # has an "http-quiv" attribute with a value of "refresh"
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
