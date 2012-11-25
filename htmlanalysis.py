##
# Internal Functions for HTML Analysis
##

from pyquery import PyQuery
from lxml import etree
import urllib
import re

def analyzeHtml(html):
  doc = PyQuery(html)
  return {
    'numChars': len( html ),
    'numIframes': len( doc('iframe') ),
    'numScripts': len( doc('script') ),
    'numScriptsWithWrongExtension': countScriptsWithWrongExtension(doc),
    'numEmbeds': len( doc('embed') ),
    'numObjects': len( doc('object') ),
    'numHyperlinks': len( doc('a') ),
    'numMetaRefresh': countMetaRefresh(doc)
  }

def isRefresh():
  httpEquiv = PyQuery(this).attr['http-equiv']
  return ( httpEquiv and httpEquiv.find('refresh') )

def countMetaRefresh(doc):
  return len ( doc('meta').filter(lambda i: isRefresh()) )

findJsExtension = re.compile('\.js[#?]?.*$')

def hasWrongExtension():
  global findJsExtension
  src = PyQuery(this).attr.src;
  return ( src and (findJsExtension.search(src) == None) );

def countScriptsWithWrongExtension(doc):
  return len( doc('script').filter(lambda i: hasWrongExtension()) )