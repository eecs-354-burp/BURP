import sys
from burp_url.TLD import tlds

try:
  from urllib.parse import urlsplit
except ImportError:
  from urlparse import urlsplit

def get_tokens(url):
    """Returns a 4 tuple of sub-domain, domain, port, path"""
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
    return (subdomain, domain, parsed.port, parsed.path)

def parseURL(arg):
    url = arg;
	
    tokenizedURL = [];
	
    schemeSplit = url.split('//');
	
    pathSplit = schemeSplit[len(schemeSplit)-1].split('/', 1);
    if len(pathSplit) == 1:
        tokenizedURL.append("");
        tokenizedURL.append("");
    else:
       tokenizedURL.append(pathSplit[1]);
    
    hostname = pathSplit[0];
	
    portSplit = hostname.split(':', 1);
	
    if len(portSplit) == 1:
        tokenizedURL.insert(0, "");
    else:
        tokenizedURL.insert(0, portSplit[1]);
	
	
    hostnameSplit = portSplit[0].split('.');
    
    if hostnameSplit[len(hostnameSplit)-1].isdigit():
        tokenizedURL.insert(0, portSplit[0]);
        tokenizedURL.insert(0, "");
    else:
        domain = hostnameSplit[len(hostnameSplit)-2] + "." +hostnameSplit[len(hostnameSplit)-1];
        
        tokenizedURL.insert(0, domain);
        
        if len(hostnameSplit) > 2:
            if hostnameSplit[0] in ('www', 'ftp', 'smtp'):
                subHost = '.'.join(hostnameSplit[1:(len(hostnameSplit)-2)]);
                tokenizedURL.insert(0, subHost);
            else:
                subHost = '.'.join(hostnameSplit[0:(len(hostnameSplit)-2)]);
                tokenizedURL.insert(0, subHost);
        else:
            tokenizedURL.insert(0, "");
            
    return tokenizedURL;
	
#example
