import http.client
import socket
import whois
import sys
from pprint import pprint
from urllib.parse import urlparse

def getWhoIs(arg):
  domain = whois.query(arg.netloc);
  return domain.__dict__;

def getHttpHeaders(arg):
  httpServ = http.client.HTTPConnection(arg.netloc, 80, timeout=5)
  #httpServ.set_debuglevel(1)
  httpServ.connect()
  httpServ.request('GET', arg.path)
  
  response = httpServ.getresponse()
  headers = response.getheaders();
  
  httpServ.close()
  
  if (response.status == "302"):
    return getHttpHeaders(headers["Location"])
  
  return headers;

def getIpAddr(arg):
  return socket.gethostbyname(arg.netloc);

def parseUrl(arg):
  url = urlparse(arg);
  pprint(url);
  return url;

def main():
  
  if (len(sys.argv) != 2):
    print("Invalid number of arguments!");
    return None;
    
  #socket.setdefaulttimeout(5)
  
  arg = parseUrl(sys.argv[1]);
  
  httpHeaders = None;
  ip = None;
  whois = None;
  
  try:
    httpHeaders = getHttpHeaders(arg);
  except Exception as e:
    print("unable to get HTTP headers");
  
  try:
    whois = getWhoIs(arg);
  except Exception as e:
    print("unable to get whois")
    
    
  try:
    ip = getIpAddr(arg);
  except Exception as e:
    print("unable to get ip")
  
  res = {"httpheaders" : httpHeaders, "whois" : whois, "ip" : ip};
  pprint(res)
  return res;  

if __name__ == "__main__":
    main()
