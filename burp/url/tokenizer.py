import sys
from burp.url.TLD import tlds

try:
  from urllib.parse import urlsplit
except ImportError:
  from urlparse import urlsplit

def getTokens(url):
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
  
  
