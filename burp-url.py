import httplib

httpServ = httplib.HTTPConnection("www.google.com", 80)
httpServ.connect()
httpServ.request('GET', "/index.html")

response = httpServ.getresponse()
if response.status == httplib.OK:
	print response.read()
	
httpServ.close()
