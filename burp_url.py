import httplib
import socket
import whois
import sys
from pprint import pprint
from urlparse import urlparse
import urlTokenizer

def getDomain(url):
  tokens = urlTokenizer.get_tokens(url)
  return tokens[1]

def getWhoIs(dom):
  ws = whois.query(dom)
  #print(ws);
  return ws.__dict__;

def getHttpHeaders(arg):
  httpServ = httlib.HTTPConnection(arg.netloc, 80, timeout=2)
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
