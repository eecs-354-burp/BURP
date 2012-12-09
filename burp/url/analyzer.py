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
  res = opener.open(HeadRequest(url))
  res.close()
  return res.info().__dict__


def getIpAddr(dom):
  """Return the ip address of the domain"""
  return socket.gethostbyname(dom);
