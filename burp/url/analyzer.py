import socket
import whois
import sys
from burp.url.TLD import tlds

try:
  from urllib.parse import urlsplit
except ImportError:
  from urlparse import urlsplit

class URLAnalyzer:
  
  def analyze(self, url):
    """ Returns a dictionary containing whois, ip and url tokens """
    tokens =  self.getTokens(url)
    return { "whois" : self.getWhoIs(tokens["domain"]), "ip" : self.getIpAddr(tokens["domain"]), "tokens" : tokens }
    
  def getWhoIs(self, dom):
    """
    Return a dictionary of whois infomation
    Will throw exception if tld server not known, or query limit reached
    """
    ws = whois.query(dom)
    print ws.__dict__
    return ws.__dict__;

  def getIpAddr(self, dom):
    """Return the ip address of the domain"""
    return socket.gethostbyname(dom);


  def getTokens(self, url):
    """Returns a dictionary of subdomain, subdomain_length, number_subdomains, domain, domain_length, port, path"""
    parsed = urlsplit(url)
    path_and_port = parsed[1].split(':')
    url_elements = path_and_port[0].split('.')
    # url_elements = ["abcde","co","uk"]
    
    domain = ""
    for i in range(-len(url_elements), 0):
      last_i_elements = url_elements[i:]
      #    i=-3: ["abcde","co","uk"]
      #    i=-2: ["co","uk"]
      #    i=-1: ["uk"] etc
      
      candidate = ".".join(last_i_elements) # abcde.co.uk, co.uk, uk
      wildcard_candidate = ".".join(["*"] + last_i_elements[1:]) # *.co.uk, *.uk, *
      exception_candidate = "!" + candidate
      
      # match tlds: 
      if (exception_candidate in tlds):
        domain =  ".".join(url_elements[i:]) 
      if (candidate in tlds or wildcard_candidate in tlds):
        domain =  ".".join(url_elements[i-1:])
        # returns "abcde.co.uk"
          
    if domain == "":
      raise ValueError("Domain not in global list of TLDs")

    subdomain = path_and_port[0].replace(domain, "").strip('.')
    num_subdomains = len(subdomain.split('.'))
    return {"subdomain" : subdomain, "subdomain_length" : len(subdomain), "number_subdomains" : num_subdomains,
            "domain" : domain, "domain_length": len(domain), "port" : parsed.port, "path" : parsed.path }
  

