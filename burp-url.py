import http.client

httpServ = http.client.HTTPConnection("www.google.com", 80)
httpServ.connect()
httpServ.request('GET', "/index.html")

response = httpServ.getresponse()
if response.status == http.client.OK:
	print(response.read())
	
httpServ.close()
