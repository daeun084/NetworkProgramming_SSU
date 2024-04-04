import socket
from argparse import ArgumentParser

def server(address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(1)
    print('Run this script in another window with "-c" to connect')
    print('Listening at', sock.getsockname())

    sc, sockname = sock.accept()
    print('Accepted connection from ', sockname)

    #server can shutdown since it is not expecting to transmit
    sc.shutdown(socket.SHUT_WR)
    message = b''

    #server receive EOF from the client
    while True:
        more = sc.recv(8192)
        if not more:
            print('Received zero bytes - EOF')
            break
        print('Received {} bytes'.format(len(more)))
        message += more

    print('Message:\n')
    #Decide byte stream to ASCII
    print(message.decode('ascii'))
    sc.close()
    #Server socket closed
    sock.close()


def client(address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)

    #Client can shutdown using SHUT_RD since it is not expecting to receive any more
    #SHUT_RD sends EOF when no more message to send
    sock.shutdown(socket.SHUT_RD)

    #Encodes ASCII into bytes stream
    sock.sendall(b'Hello\n')
    sock.sendall(b'HIHIHI\n')

    sock.close()


if __name__ == '__main__':
    parser = ArgumentParser(description='Transmit & receive a data stream')
    parser.add_argument('hostname', nargs='?', default='127.0.0.1',
                        help='IP address or hostname (default: %(default)s)')
    parser.add_argument('-c', action='store_true', help='run as the client')
    parser.add_argument('-p', type=int, metavar='port', default=1060,
                        help='TCP port number (default: %(default)s')

    args = parser.parse_args()
    function = client if args.c else server
    function((args.hostname, args.p))