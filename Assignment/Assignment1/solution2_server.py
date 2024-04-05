import socket

MAX_BYTES = 1024 * 1024


def server():
    # make socket
    try:
        # use IPv4, UDP protocol
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as e:
        print("Socket Error:", e)
        exit(0)

    # bind socket
    try:
        s.bind(('127.0.0.1', 8080))
    except socket.error as e:
        print("Bind Error:", e)
        exit(0)

    # listening client
    server_ip, server_port = s.getsockname()
    print('Server listening on {}:{}...'.format(server_ip, server_port))

    # recv data from client
    try:
        data, addr = s.recvfrom(MAX_BYTES)
        text = data.decode('utf-8')

        # client's address parsing
        client_ip, client_port = addr

        # doubling every vowel in the received message
        double_text = doubling_text(text)
        print("Sent modified message back to ('{}', {}): {}".format(client_ip, client_port, double_text))

        # resend data to client
        s.sendto(double_text.encode('utf-8'), (client_ip, client_port))

    except socket.error as e:
        print("Socket Error while receiving data:", e)
        exit(0)

    # close socket
    s.close()


def doubling_text(text):
    # doubling every vowel in the message
    vowels = 'aeiouAEIOU'
    result = ''

    for char in text:
        if char in vowels:
            # doubling vowels
            result += char * 2
        else:
            result += char
    return result


if __name__ == '__main__':
    server()
