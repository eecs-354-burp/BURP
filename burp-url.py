import http.client
import socket
import whois

print(socket.gethostbyname('www.google.com'))

with open("sample-urls") as urlsFile:
	for line in urlsFile:
		line = line.rstrip()
		print(line)
		print(socket.gethostbyname(line))

		httpServ = http.client.HTTPConnection(line, 80)
		httpServ.connect()
		httpServ.request('GET', "/")

		response = httpServ.getresponse()

		if response.status == http.client.OK:
			print(response.getheaders())
						
		httpServ.close()

