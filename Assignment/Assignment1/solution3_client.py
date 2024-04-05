import socket

win_comment = 'Congratulations you did it.\n'
end_comment = "User don't start Game! End the Connection\n"
attempt_comment = 'The Attempt to play is over. End the connection\n'


def client():
    # make socket
    try:
        # use IPv4, TCP protocol
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("Socket Error:", e)
        exit(0)

    # set timeout to udp socket
    s.settimeout(5)

    # connect socket
    try:
        s.connect(('127.0.0.1', 8080))
    except socket.error as e:
        print("Socket Connection Error:", e)
        exit(0)

    # get response
    while True:
        try:
            response = s.recv(2048).decode('utf-8')
        except socket.timeout as e:
            # catch timeout error
            print("Timeout occurred while receiving data", e)
            break
        except ConnectionResetError as e:
            # catch reset error
            print("Connection with server reset:", e)
            break

        # print the response message to client
        print(response)

        # case for client success to guess num and win
        # or case for client don't start the game
        # or case for attempt for game is over
        if (response.__eq__(win_comment)
                or response.__eq__(end_comment)
                or attempt_comment in response):
            break

        # accept the input for request and guess num
        request = input()
        s.sendall(request.encode('utf-8'))

    # close socket connection
    s.close()


if __name__ == '__main__':
    client()
