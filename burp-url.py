import http.client
import socket
import whois
import sys

def getWhoIs(arg):
  domain = whois.query('domain '+arg);
  return domain.__dict__;

def getHttpHeaders(arg):
  httpServ = http.client.HTTPConnection(arg, 80)
  httpServ.connect()
  httpServ.request('GET', "/")

  response = httpServ.getresponse()
  print(response.status);
  headers = response.getheaders();
  
  httpServ.close()
  
  return headers;

def getIpAddr(arg):
  return socket.gethostbyname(arg);

def main():
  arg = sys.argv[1];
  httpHeaders = getHttpHeaders(arg);
  whois = getWhoIs(arg);
  ip = getIpAddr(arg);
  res = {"httpheaders" : httpHeaders, "whois" : whois, "ip" : ip};
  print(res)
  return res;  

if __name__ == "__main__":
    main()
