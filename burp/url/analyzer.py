import socket
import whois
import sys
from pprint import pprint
from burp.url.tokenizer import getTokens

def getWhoIs(dom):
  """Return a dictionary of whois infomation
  Will throw exception if tld server not known, or query limit reached
  """
  ws = whois.query(dom)
  #print(ws);
  return ws.__dict__;

def getIpAddr(dom):
  """Return the ip address of the domain"""
  return socket.gethostbyname(dom);
