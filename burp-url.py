import http.client
import socket


print(socket.gethostbyname('www.google.com'))

with open("sample-urls") as urlsFile:
	for line in urlsFile:
		print(line.rstrip())
		print(socket.gethostbyname(line.rstrip()))
		

httpServ = http.client.HTTPConnection("www.google.com", 80)
httpServ.connect()
httpServ.request('GET', "/index.html")

response = httpServ.getresponse()

if response.status == http.client.OK:
	print(response.getheaders())

	
httpServ.close()
