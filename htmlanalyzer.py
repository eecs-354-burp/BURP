##
# Internal Functions for HTML Analysis
##

from pyquery import PyQuery
from pyquery.openers import url_opener
from lxml import etree
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

  findUrlDomain = re.compile('^(?:http[s]?|ftp):\/\/(?:www\.)?([^:\/\s]+)')

  isKnownElement = re.compile('a|abbr|acronym|address|applet|area|article|aside|audio|b|base|basefont|bdi|bdo|big|blockquote|body|br|button|canvas|caption|center|cite|code|col|colgroup|command|datalist|dd|del|details|dfn|dir|div|dl|dt|em|embed|fieldset|figcaption|figure|font|footer|form|frame|frameset|h1|h2|h3|h4|h5|h6|head|header|hgroup|hr|html|i|iframe|img|input|ins|kbd|keygen|label|legend|li|link|map|mark|menu|meta|meter|nav|nobr|noframes|noscript|object|ol|optgroup|option|output|p|param|pre|progress|q|rp|rt|ruby|s|samp|script|section|select|small|source|span|strike|strong|style|sub|summary|sup|table|tbody|td|textarea|tfoot|th|thead|time|title|tr|track|tt|u|ul|var|video|wbr')

  smallElementAreaThreshold = 30; # px ^ 2

  smallElementDimensionThreshold = 2; # px

  def __init__(self, url=''):
    if url:
      self.setUrl(url)
      # Use PyQuery's URL opener to properly handle content encoding
      html = str( url_opener(url, {}).read() )
      self.load(html)

  ##
  # Loads the given HTML string for analysis
  ##
  def load(self, html):
    # Must use 'html' parser to handle poorly-formatted HTML
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

    elems = self.doc('*')
    numElements = len( elems )
    numUnknownElements = self.countUnknownElements()

    unsafeUrls = self.getUnsafeIncludedUrls()
    safeUrls = self.getSafeIncludedUrls()
    externalUrls = [url for url in (unsafeUrls + safeUrls) if self.isExternalUrl(url)] 

    return {
      'numChars': numChars,
      'percentWhitespace': self.getPercentage(numWhitespaceChars, numChars),
      'percentScriptChars': self.getPercentage(numScriptChars, numChars),
      'numIframes': self.countElems('iframe'),
      'numScripts': self.countElems('script'),
      'numScriptsWithWrongExtension': self.countElems('script', self.hasWrongExtension),
      'numEmbeds': self.countElems('embed'),
      'numObjects': self.countElems('object'),
      'numHyperlinks': self.countElems('a'),
      'numMetaRefresh': self.countElems('meta', self.isRefresh),
      'numHiddenElements': self.countElems('*', self.isHidden),
      'numSmallElements': self.countElems('*', self.isSmall),
      'hasDoubleDocuments': self.hasDoubleDocuments(),
      'numUnsafeIncludedUrls': len( unsafeUrls ),
      'numExternalUrls': len( externalUrls ),
      'percentUnknownElements': self.getPercentage(numUnknownElements, numElements),
    }

  ##
  # Returns the percentage of a / b
  ##
  def getPercentage(self, a, b):
    return ( float(a) / float(b) ) * 100

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
    return ( httpEquiv and httpEquiv.find('refresh') > -1 )

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
    if (width != None) and (height != None):
      return (width * height) < self.smallElementAreaThreshold;
    else:
      return ( (width != None and (width <= self.smallElementDimensionThreshold)) or
               (height != None and (height <= self.smallElementDimensionThreshold)) )

  ##
  # Returns true if the document has more than one html, head, title, or body element
  ##
  def hasDoubleDocuments(self):
    for tagName in ['html', 'head', 'title', 'body']:
      if (len( self.doc(tagName) ) > 1) : return True
    return False

  ##
  # Returns an array of the values for the given attribute in elements with the given tag names
  ##
  def getAttrValues(self, tagNames, attr):
    return self.doc(tagNames).map(lambda i: PyQuery(this).attr[attr])

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
      return (domain == self.domain)
    else:
      return False

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
  # Returns the number of unknown HTML elements
  ##
  def countUnknownElements(self):
    return len( [elem for elem in self.doc('*') if self.isKnownElement.match(elem.tag) == None] )

