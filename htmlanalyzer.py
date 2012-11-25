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

  def load(self, html):
    self.html = html
    self.doc = PyQuery(html)

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

  def countElems(self, elem, f = None):
    if f:
      return len( self.doc(elem).filter(lambda i: f()) )
    else:
      return len( self.doc(elem) )

  def isRefresh(self):
    httpEquiv = PyQuery(this).attr['http-equiv']
    return ( httpEquiv and httpEquiv.find('refresh') )

  def hasWrongExtension(self):
    src = PyQuery(this).attr['src'];
    return ( src and (self.findJsExtension.search(src) == None) );
