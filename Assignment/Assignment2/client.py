import socket
import json

win_comment = 'Congratulations, you did it.\n'
end_comment = "User don't start Game! End the Connection\n"
attempt_comment = "Sorry, you've used all your attempts!\n"

MAX_BYTES = 1024 * 1024


def client():
    # make socket
    s = make_socket()

    # set timeout to udp socket
    s.settimeout(5)

    # connect socket
    connect_socket(s)

    # get response
    while True:
        try:
            deserialized_response = s.recv(MAX_BYTES)
            response = load_json(deserialized_response)

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

        # check the response message
        if check_comment(response):
            break

        # accept the input for request and guess num
        send_request(s)

    # close socket connection
    close_socket(s)


def make_socket():
    try:
        # use IPv4, TCP protocol
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("Socket Error:", e)
        exit(0)
    return s


def connect_socket(s):
    try:
        s.connect(('127.0.0.1', 8080))
        print('Connected to {}:{}'.format(s.getpeername()[0], s.getpeername()[1]))
    except socket.error as e:
        print("Socket Connection Error:", e)
        exit(0)


def send_request(s):
    deserialized_request = input()
    request = dump_json(deserialized_request)
    s.sendall(request)


def dump_json(data):
    try:
        serialized_data = json.dumps(data).encode('utf-8')
    except TypeError as e:
        print("Type Error:", e)
        exit(0)
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        exit(0)
    return serialized_data


def load_json(data):
    try:
        deserialized_data = json.loads(data.decode('utf-8'))
    except TypeError as e:
        print("Type Error:", e)
        exit(0)
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        exit(0)
    return deserialized_data


def close_socket(s):
    print("Connection Closed")
    s.close()


def check_comment(response):
    # case for client success to guess num and win
    # or case for client don't start the game
    # or case for attempt for game is over
    if (response.__eq__(win_comment)
            or response.__eq__(end_comment)
            or attempt_comment in response):
        return True
    else:
        return False


if __name__ == '__main__':
    client()
