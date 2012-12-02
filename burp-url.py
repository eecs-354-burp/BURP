import http.client
import socket
import whois
import sys
from pprint import pprint
from urllib.parse import urlparse

def getDomain(arg):
  argList = arg.split(".");
  
  if len(argList) < 2:
    return argList[0];
    
  tlds = open("tlds_nocomments.txt");
  
  buf = tlds.read();
  res = None;
  
  if argList[-1] in buf:
    res = argList[-2]+"."+argList[-1];
  
  if argList[-2]+"."+argList[-1] in buf:
    res = argList[-3]+"."+argList[-2]+"."+argList[-1];
  
  print("res = " + res);
  tlds.close();
  
  if res == None:
    raise Exception;
  else:
    return res;

def getWhoIs(dom):
  ws = whois.query(dom)
  print(ws);
  return ws.__dict__;

def getHttpHeaders(arg):
  httpServ = http.client.HTTPConnection(arg.netloc, 80, timeout=2)
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

def main():
  
  if (len(sys.argv) != 2):
    print("Invalid number of arguments!");
    return None;
    
  #socket.setdefaulttimeout(5)
  
  arg = parseUrl(sys.argv[1]);
  
  httpHeaders = None;
  ip = None;
  whois = None;
  domain = getDomain(arg.netloc)
  print(domain)
  try:
    ip = getIpAddr(domain);
  except Exception as e:
    print("unable to get ip")
  
  try:
    httpHeaders = getHttpHeaders(arg);
  except Exception as e:
    print("unable to get HTTP headers");
  
  try:
    if (ip != None):
      whois = getWhoIs(domain);
  except Exception as e:
    print("unable to get whois")
  
  #iptwhois = getWhoIs(domain);
  
  res = {"httpheaders" : httpHeaders, "whois" : whois, "ip" : ip};
  pprint(res)
  return res;  

if __name__ == "__main__":
    main()
