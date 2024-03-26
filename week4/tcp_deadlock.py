import socket
import sys


def server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(1)
    print('Listening at', sock.getsockname())
    while True:
        sc, sockname = sock.accept()
        print('Processing up to 1024 bytes at a time from', sockname)
        n = 0
        while True:
            #receive and process 1024 bytes at a time
            #to not to overwhelm the memory
            data = sc.recv(1024)
            if not data:
                break
            #decode byte stram to ASCII
            output = data.decode('ascii').upper().encode('ascii')
            sc.sendall(output)
            n+= len(data)
            print('\r %d bytes processed so far' % (n,), end=' ')
            sys.stdout.flush()
        print()
        sc.close()
        print('Socket closed')
def client(host, port, bytecount):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #round up to a multiple of 16
    #size of message
    bytecount = (bytecount + 15) // 16 * 16
    #send message to server
    message = b'capitalize this!'

    print('Sending', bytecount, 'bytes of data, in chunks of 16 bytes')
    sock.connect((host, port))

    sent = 0
    #repeatedly send 16 byte message up to the specified byte count
    while sent < bytecount:
        sock.sendall(message)
        sent += len(message)
        print('\r %d bytes sent' % (sent,), end=' ')
        sys.stdout.flush()

    print()
    #shutdown socket WRITE
    sock.shutdown(socket.SHUT_WR)
    print('Receiving all the data the server sends back')

    received = 0
    while True:
        #receive up to 42byte from the server at each iteration
        data = sock.recv(42)
        if not received:
            #thr first 42 bytes of received data
            print('The first data received says', repr(data))
        if not data:
            break
        received += len(data)
        #print the number of bytes received so far
        print('\r %d bytes received' % (received,), end=' ')

    print()
    sock.close()


