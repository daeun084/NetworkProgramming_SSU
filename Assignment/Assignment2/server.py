import random
import socket
import json
import ssl
import argparse

# comment for client
win_comment = 'Congratulations, you did it.\n'
up_comment = 'Hint: You Guessed too high!\n'
down_comment = 'Hint: You guessed too small!\n'
start_comment = 'Guess the Number! Would you start the game?: '
end_comment = "User don't start Game! End the Connection\n"
attempt_comment = "Sorry, you've used all your attempts!\n"
guess_comment = '[Guess the number]: '
invalid_input_error_comment = 'Invalid Guess Num. Try again\n'
server_response_buffer = ''

MAX_BYTES = 1024 * 1024


def server(cafile, certfile):
    # make socket
    s = make_socket()

    # bind socket
    bind_socket(s)

    # listen socket
    listen_socket(s)

    # accept client socket
    sc = accept_socket(s)

    # make socket with ssl
    sc = make_ssl_socket(sc, certfile, cafile)

    # inform client about game and recv 'start'
    serialized_start_comment = dump_json(start_comment)
    sc.sendall(serialized_start_comment)

    try:
        deserialized_start_request = sc.recv(MAX_BYTES)
        start_request = load_json(deserialized_start_request)

        if start_request == 'start':
            # if client input start, start the number game
            guess_number_game(sc)
        else:
            # if client doesn't input start, end the connection
            end_connection(s, sc)
    except socket.error as e:
        print("Socket Error while receiving message:", e)

    # close socket connection
    close_socket(s, sc)


def guess_number_game(sc):
    global server_response_buffer
    print("Start the Number Guess Game")

    # count for client's attempt
    count = 0

    # make random number
    x = random.randint(1, 10)

    # client attempt 5 under
    while count < 5:
        # send client for guess the number question
        serialized_guess_request = dump_json(server_response_buffer + guess_comment)
        sc.sendall(serialized_guess_request)

        # init response buffer
        server_response_buffer = ''

        # recv from client the guess number And parse it to int
        try:
            response = sc.recv(MAX_BYTES)
            guess = int(load_json(response))
        except ValueError as e:
            invalid_input_error()
            continue

        # filtering the input number range
        if guess > 10 or guess < 1:
            invalid_input_error()
            continue

        # print guess number from client
        print("[Client's Guess Number]: ", guess)

        # compare the guess num and the random num
        if guess == x:
            sc.sendall(dump_json(win_comment))
            print('The Client win the Game. End the connection')
            return
        elif guess < x:
            server_response_buffer += down_comment
        elif guess > x:
            server_response_buffer += up_comment

        # check attempt count
        count += 1

    # if client's attempt is over
    if server_response_buffer == '':
        sc.sendall(dump_json(attempt_comment))
    else:
        sc.sendall(dump_json(server_response_buffer + attempt_comment))
    print(attempt_comment)


def make_ssl_socket(sc, certfile, cafile):
    # make context
    purpose = ssl.Purpose.SERVER_AUTH
    # specify the purpose and protocol
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER, cafile=cafile)
    context.purpose = purpose
    context.check_hostname = False
    context.load_cert_chain(certfile=certfile) # use PEM file

    # return server's wrapped socket
    return context.wrap_socket(sc, server_side=True)


def make_socket():
    try:
        # use IPv4, TCP protocol
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as e:
        print("Socket Error:", e)
        exit(0)
    return s


def bind_socket(s):
    try:
        s.bind(('127.0.0.1', 8080))
    except socket.error as e:
        print("Bind Error:", e)
        exit(0)


def listen_socket(s):
    try:
        s.listen(1)
        print('Listening on {}:{}'.format(s.getsockname()[0], s.getsockname()[1]))
    except socket.error as e:
        print("Listen Error:", e)
        exit(0)


def accept_socket(s):
    try:
        sc, addr = s.accept()
        # print address of client
        print('Accepted connection from {}:{}'.format(addr[0], addr[1]))
    except socket.error as e:
        print("Socket Accept Error:", e)
        exit(0)
    return sc


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


def invalid_input_error():
    global server_response_buffer
    print(invalid_input_error_comment)
    server_response_buffer += invalid_input_error_comment


def close_socket(s, sc):
    print("Connection Closed")
    sc.close()
    s.close()


def end_connection(s, sc):
    serialized_end_comment = dump_json(end_comment)
    sc.sendall(serialized_end_comment)
    print(end_comment)
    close_socket(s, sc)
    exit(0)


if __name__ == '__main__':
    # set argument for pem file
    parser = argparse.ArgumentParser(description='Server for Number Guess Game')
    parser.add_argument('-a', metavar='cafile', default=None)
    parser.add_argument('-s', metavar='certfile', default=None)
    args = parser.parse_args()

    server(args.a, args.s)
