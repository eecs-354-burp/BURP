#Input: A URL
#Output: A list with entries: subhost,domain,port,path

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
result = parseURL("70.33.246.30/~impre264/.bin/bb30/server/cp.php?m=login");
print(result);
	

