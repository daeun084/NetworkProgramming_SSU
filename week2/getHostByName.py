import socket
if __name__ == '__main__':
    hostname = 'cse.ssu.ac.kr'
    addr = socket.gethostbyname(hostname)
    print('The IP address of {} is {}'.format(hostname, addr))

