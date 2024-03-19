import argparse, random, socket, sys
MAX_BYTES = 655375

def server(interface, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(interface, port)
    print('Listening for datagrams at {}'.format(sock.getsockname()))
    while True:
        data, address = sock.recvfrom(MAX_BYTES)
        if random.random() < 0.5:
            print('Pretending to drop packet from {}'.format(address))
            continue
        text = data.decode('ascii')
        print('The client at {} says: {!r}'.format(address, text))
        message = 'Your data was {} byte Long'.format(len(data))
        sock.sendto(message.encode('ascii'), address)

def client(hostname, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((hostname, port))
    print('Client socket name is {}'.format(sock.getsockname()))

    #set blocking
    delay = 0.1
    text = 'This is another message'
    data = text.encode('ascii')
    while True:
        sock.send(data)
        print('Waiting up to {} seconds for a reply'.format(delay))
        sock.settimeout(delay) #set delay, backofftime
        try:
            data = sock.recv(MAX_BYTES)
        except sock.timeout as exc:
            delay *= 2 #backoff
            if delay > 2.0 :
                raise RuntimeError('I think the server is down') from exc
            else:
                break

if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description='Send, receive UDP broadcast')
    parser.add_argument('role', choices=choices, help='which role to take')
    parser.add_argument('host', help='interface the server listens at;'
                        ' network the client sends to')
    parser.add_argument('-p', metavar='port', type=int, default=1060,
                        help='UDP port (default: 1060)')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.host, args.p)


