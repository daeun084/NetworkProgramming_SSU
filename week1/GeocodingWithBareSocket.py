import socket
import ssl #secure socket layer
from urllib.parse import quote_plus

#GET request
request_text = """\
GET /search?q={}&format=json HTTP/1.1\r\n\
Host: nominatim.openstreetmap.org\r\n\
User-Agent: Daeun\r\n\
Connectioin : close\r\n\
"""

def geocode(address):
    unencrypted_sock = socket.socket() #create new socket
    # bind socket
    unencrypted_sock.connect(('nominatim.openstreetmap.org', 443)) # ip address and port number
    sock = ssl.wrap_socket(unencrypted_sock) #wrap

    request = request_text.format(quote_plus(address))
    print(request)

    #send request
    sock.sendall(request.encode('ascii'))
    raw_reply = b''
    while True:
        more = sock.recv(4096) #receive byte on port number 4096
        if not more:
            break
        raw_reply += more

    print(raw_reply.decode('utf-8'))
    print(raw_reply)

if __name__ == '__main__':
    geocode('Soongsil University')