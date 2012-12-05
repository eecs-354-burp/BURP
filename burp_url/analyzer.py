import socket
import whois
import sys
from pprint import pprint
import tokenizer

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

def getDomain(url):
  tokens = tokenizer.get_tokens(url)
  return tokens[1]

def getWhoIs(dom):
  ws = whois.query(dom)
  #print(ws);
  return ws.__dict__;

class HeadRequest(Request):
    def get_method(self):
        return 'HEAD'

def getheadersonly(url, redirections=True):
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
    return res.info()

def getHttpHeaders(arg):
  httpServ = HTTPConnection(arg.netloc, 80, timeout=2)
  #httpServ.set_debuglevel(1)
  httpServ.connect()
  httpServ.request('GET', arg.path)
  
  response = httpServ.getresponse()
  headers = response.getheaders();
  
  httpServ.close()
  
  if (response.status == "302"):
    return getHttpHeaders(headers["Location"])
  
  return headers;

def getIpAddr(dom):
  return socket.gethostbyname(dom);

def parseUrl(arg):
  url = urlparse(arg);
  #pprint(url);
  return url;


def whois_headers(url, domain):
  arg = parseUrl(url);
  
  httpHeaders = None;
  ip = None;
  whois = None;
  try:
    ip = getIpAddr(domain);
  except Exception as e:
    pass
  
  try:
    httpHeaders = getHttpHeaders(arg);
  except Exception as e:
    pass
  
  try:
    if (ip != None):
      whois = getWhoIs(domain);
  except Exception as e:
    pass
  
  #iptwhois = getWhoIs(domain);
  
  res = {"httpheaders" : httpHeaders, "whois" : whois, "ip" : ip};
  return res;  

if __name__ == "__main__":
    main()
