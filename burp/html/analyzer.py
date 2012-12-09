##
# Internal Functions for HTML Analysis
##

from pyquery import PyQuery
from pyquery.openers import url_opener
from lxml import etree

# Import list of suspicious object classids from PhoneyC
# (http://code.google.com/p/phoneyc/)
from .CLSID import clsidlist

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

  findCLSID = re.compile('clsid:(.+)')

  findNumber = re.compile('([\.\d-]+)')

  findUrlDomain = re.compile('^(?:http[s]?|ftp):\/\/(?:www\.)?([^:\/\s]+)')

  knownElements = [ 'a', 'abbr', 'acronym', 'address', 'applet', 'area', 'article', 'aside', 'audio', 'b', 'base', 'basefont', 'bdi    ', 'bdo', 'big', 'blockquote', 'body', 'br', 'button', 'canvas', 'caption', 'center', 'cite', 'code', 'col', 'colgroup', 'command', 'datalist', 'dd', 'del', 'details    ', 'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'embed', 'fieldset', 'figcaption', 'figure', 'font', 'footer', 'form', 'frame', 'frameset', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'h    eader', 'hgroup', 'hr', 'html', 'i', 'iframe', 'img', 'input', 'ins', 'kbd', 'keygen', 'label', 'legend', 'li', 'link', 'map', 'mark', 'menu', 'meta', 'meter', 'nav', 'nobr', 'n    oframes', 'noscript', 'object', 'ol', 'optgroup', 'option', 'output', 'p', 'param', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby', 's', 'samp', 'script', 'section', 'selec    t', 'small', 'source', 'span', 'strike', 'strong', 'style', 'sub', 'summary', 'sup', 'table', 'tbody', 'td', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title', 'tr', 'tr    ack', 'tt', 'u', 'ul', 'var', 'video', 'wbr' ]

  smallElementAreaThreshold = 30 # px ^ 2

  smallElementDimensionThreshold = 2 # px

  ##
  # Initialization Methods
  ##

  def __init__(self, url=''):
    if url:
      self.loadUrl(url)

  ##
  # Loads the HTML at the given URL for analysis
  ##
  def loadUrl(self, url):
    self.setUrl(url)
    # Use PyQuery's URL opener to properly handle content encoding
    html = str( url_opener(url, {}).read() )
    self.loadHtml(html)

  ##
  # Loads the given HTML string for analysis
  ##
  def loadHtml(self, html):
    # Must use 'html' parser to handle invalid HTML
    self.doc = PyQuery(html, parser='html')
    self.html = html

  ##
  # Sets the internal url and domain properties to match the given URL
  ##
  def setUrl(self, url):
    self.url = url
    self.domain = self.findUrlDomain.search(url).group(1)

  ##
  # Returns a dictionary with the analysis results
  ##
  def analyze(self):
    numChars = len( self.html )
    numWhitespaceChars = self.countWhitespaceChars()
    numScriptChars = self.countScriptChars()

    numElements = len( self.doc('*') )
    numUnknownElements = self.countElems('*', self.isUnknownElement)

    unsafeUrls = self.getUnsafeIncludedUrls()
    safeUrls = self.getSafeIncludedUrls()
    externalUrls = [url for url in (unsafeUrls + safeUrls) if self.isExternalUrl(url)] 

    return {
      'numCharacters': numChars,
      'percentWhitespace': self.getPercentage(numWhitespaceChars, numChars),
      'percentScriptContent': self.getPercentage(numScriptChars, numChars),
      'numIframes': self.countElems('iframe'),
      'numScripts': self.countElems('script'),
      'numScriptsWithWrongExtension': self.countElems('script', self.hasWrongExtension),
      'numEmbeds': self.countElems('embed'),
      'numObjects': self.countElems('object'),
      'numSuspiciousObjects': self.countElems('object', self.isSuspiciousObject),
      'numHyperlinks': self.countElems('a'),
      'numMetaRefresh': self.countElems('meta', self.isMetaRefresh),
      'numHiddenElements': self.countElems('*', self.isHidden),
      'numSmallElements': self.countElems('*', self.isSmall),
      'hasDoubleDocuments': self.hasDoubleDocuments(),
      'numUnsafeIncludedUrls': len( unsafeUrls ),
      'numExternalUrls': len( externalUrls ),
      'percentUnknownElements': self.getPercentage(numUnknownElements, numElements)
    }

  ##
  # Helper Methods
  ##

  ##
  # Returns the percentage of a / b
  ##
  def getPercentage(self, a, b):
    return ( float(a) / float(b) ) * 100

  ##
  # Returns an array of the values for the given attribute in elements with the given tag names
  ##
  def getAttrValues(self, tagNames, attr):
    return self.doc(tagNames).map(lambda i: PyQuery(this).attr[attr])

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
  # Character-Counting Methods
  ##

  ##
  # Returns the number of whitespace characters
  ##
  def countWhitespaceChars(self):
    return len( re.findall('\s', self.html) )

  ##
  # Returns the number of characters of inline script content
  ##
  def countScriptChars(self):
    return sum(len(script) for script in self.doc('script').contents())

  ##
  # Element-Counting Methods
  ##

  ##
  # Counts the number of elements matching the given tag name,
  # optionally filtered by a function
  ##
  def countElems(self, tagName, f = None):
    if f:
      return len( self.doc(tagName).filter(lambda i, this: f(this)) )
    else:
      return len( self.doc(tagName) )

  ##
  # Returns true if the document has more than one html, head, title, or body element
  ##
  def hasDoubleDocuments(self):
    for tagName in ['html', 'head', 'title', 'body']:
      if (len( self.doc(tagName) ) > 1) : return True
    return False

  ##
  # PyQuery Filter Functions
  ##

  ##
  # Returns true if the PyQuery element (this)
  # has an "http-equiv" attribute with a value of "refresh"
  ##
  def isMetaRefresh(self, this):
    httpEquiv = PyQuery(this).attr['http-equiv']
    return ( httpEquiv and httpEquiv.find('refresh') > -1 )

  ##
  # Returns true if the PyQuery element (this)
  # has a classid found in clsidlist
  ##
  def isSuspiciousObject(self, this):
    classidAttr = PyQuery(this).attr['classid']
    if classidAttr:
      match = self.findCLSID.match(classidAttr)
      if match:
        clsid = match.group(1)
        return ( clsid and clsid in clsidlist )
    return False

  ##
  # Returns true if the PyQuery element (this)
  # has a "src" attribute that points to a URI without a "js" extension
  ##
  def hasWrongExtension(self, this):
    src = PyQuery(this).attr['src']
    return ( src and (self.findJsExtension.search(src) == None) )

  ##
  # Returns true if the PyQuery element (this)
  # has its CSS style set to "display: none" or "visibility: hidden"
  ##
  def isHidden(self, this):
    style = PyQuery(this).attr['style']
    return ( style and (self.findHiddenStyle.search(style) != None) )

  ##
  # Returns true if the area, width, or height of the PyQuery element (this)
  # are smaller than predetermined thresholds
  ##
  def isSmall(self, this):
    elem = PyQuery(this)
    width = self.getDimension(elem, 'width')
    height = self.getDimension(elem, 'height')
    if (width != None) and (height != None):
      return (width * height) < self.smallElementAreaThreshold
    else:
      return ( (width != None and (width < self.smallElementDimensionThreshold)) or
               (height != None and (height < self.smallElementDimensionThreshold)) )

  ##
  # Returns true if the PyQuery element (this) is a valid HTML element
  ##
  def isUnknownElement(self, this):
    return ( len(this) > 0 ) and ( this[0].tag not in self.knownElements )

  ##
  # URL-Analysis Methods
  ##

  ##
  # Returns an array of the URLs for external content that are included 
  # by elements that can be used to include executable code
  ##
  def getUnsafeIncludedUrls(self):
    urls = ( self.getAttrValues('script, iframe, frame, embed', 'src') + 
             self.getAttrValues('form', 'action') +
             self.getAttrValues('object', 'data') )
    # Remove empty strings
    return [url for url in urls if url] 

  ##
  # Returns an array of the URLs for external content that are included
  # by elements that CANNOT be used to include executable code
  ##
  def getSafeIncludedUrls(self):
    urls = ( self.getAttrValues('img', 'src') + self.getAttrValues('link', 'href') )
    # Remove empty strings
    return [url for url in urls if url] 

  ##
  # Returns true if the given URL has a different domain than the current document
  ##
  def isExternalUrl(self, url):
    match = self.findUrlDomain.search(url)
    if match:
      domain = match.group(1)
      return (domain != self.domain)
    else:
      return False
