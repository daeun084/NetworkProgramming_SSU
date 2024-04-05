import socket

MAX_BYTES = 1024 * 1024


def client():
    # make socket
    try:
        # use IPv4, UDP protocol
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as e:
        print("Socket Error:", e)
        exit(0)

    # set timeout to udp socket
    s.settimeout(5)

    # send message
    sendmsg = input("Enter message to send to server: ")
    s.sendto(sendmsg.encode('utf-8'), ('127.0.0.1', 8080))

    # get response
    try:
        data, address = s.recvfrom(MAX_BYTES)

        # decode response
        response = data.decode('utf-8')
        print('Received modified message from server: ' + response)

    except socket.timeout:
        # catch timeout error
        print("Timeout occurred while receiving data")
        exit(0)

    # close connection
    s.close()


if __name__ == '__main__':
    client()
