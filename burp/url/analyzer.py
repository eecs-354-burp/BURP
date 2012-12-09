import socket
import whois
import sys
from pprint import pprint
from burp.url.tokenizer import getTokens

try:
  from http.client import HTTPConnection
except ImportError:
  from httplib import HTTPConnection

try:
  from urllib.request import Request, OpenerDirector, HTTPHandler, HTTPDefaultErrorHandler, HTTPErrorProcessor, HTTPRedirectHandler
except ImportError:
  from urllib2 import Request, OpenerDirector, HTTPHandler, HTTPDefaultErrorHandler, HTTPErrorProcessor, HTTPRedirectHandler

try:
  from urllib.parse import urlparse
except ImportError:
  from urlparse import urlparse

try:
  from urllib.error import HTTPError
except ImportError:
  from urllib2 import HTTPError


def getWhoIs(dom):
  """Return a dictionary of whois infomation
  Will throw exception if tld server not known, or query limit reached
  """
  ws = whois.query(dom)
  #print(ws);
  return ws.__dict__;

class HeadRequest(Request):
  """Make a HEAD request for a given url, inherits from urllib.request.Request"""
  def get_method(self):
    return 'HEAD'

def getHttpHeaders(url, redirections=True):
  """Return a dictionary of the headers for the site at url"""
  opener = OpenerDirector()
  opener.add_handler(HTTPHandler())
  opener.add_handler(HTTPDefaultErrorHandler())
  if redirections:
    # HTTPErrorProcessor makes HTTPRedirectHandler work
    opener.add_handler(HTTPErrorProcessor())
    opener.add_handler(HTTPRedirectHandler())
  try:
    res = opener.open(HeadRequest(url))
  except HTTPError as res:
    pass
  res.close()
  return res.info().dict


def getIpAddr(dom):
  """Return the ip address of the domain"""
  return socket.gethostbyname(dom);


def allInfo(url):
  """Returns a dict of http headers, ip address, and whois information"""
  domain = getTokens(url)[1]
  arg = urlparse(url)
  
  httpHeaders = None
  ip = None
  whois = None
  try:
    ip = getIpAddr(domain)
  except Exception as e:
    pass
  
  try:
    httpHeaders = getHttpHeaders(url)
  except Exception as e:
    pass
  
  try:
    if ip is not None:
      whois = getWhoIs(domain)
  except Exception as e:
    pass
  
  
  res = {"httpheaders" : httpHeaders, "whois" : whois, "ip" : ip};
  return res;  

if __name__ == "__main__":
  if not len(sys.argv) == 2:
    print("Usage: " + sys.argv[0] + " [URL]")
    exit(1)
  url = sys.argv[1]
  domain = getTokens(url)[1]
  print( whois_headers(url, domain) )
