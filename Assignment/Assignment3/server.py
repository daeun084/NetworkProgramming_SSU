import random, socket, json, ssl, argparse, zlib, pickle, memcache, logging


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
history_data = ''

MAX_BYTES = 1024 * 1024
logger = logging.getLogger('server')


def server(certfile, cafile=None):
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
    send_to_client(sc, start_comment)

    try:
        deserialized_start_request = sc.recv(MAX_BYTES)
        start_request = load_json(deserialized_start_request)
        save_history_data(start_request + '\n')

        if start_request == 'start':
            # print history data
            print("-----HISTORY START-----")
            loaded_history_list = load_history()
            print_history(loaded_history_list)
            print("-----HISTORY END-----")

            # if client input start, start the number game
            guess_number_game(sc)
        else:
            # if client doesn't input start, end the connection
            end_connection(s, sc)
    except socket.error as e:
        logger.error("Socket Error while receiving message: %s", e)

    # close socket connection
    close_socket(s, sc)


def guess_number_game(sc):
    global server_response_buffer
    logger.info("Start the Number Guess Game")

    # count for client's attempt
    count = 0

    # make random number
    x = random.randint(1, 10)

    # client attempt 5 under
    while count < 5:
        # send client for guess the number question
        # use response buffer for send multiple comments
        send_to_client(sc, server_response_buffer + guess_comment)

        # after sending buffer's message, init response buffer
        server_response_buffer = ''

        # recv from client the guess number And parse it to int
        try:
            response = sc.recv(MAX_BYTES)
            guess = int(load_json(response))
            save_history_data(response.decode('utf-8') + '\n')
        except ValueError as e:
            invalid_input_error()
            continue

        # filtering the input number range
        if guess > 10 or guess < 1:
            invalid_input_error()
            continue

        # log guess number from client
        logger.info("[Client's Guess Number]: %s", guess)

        # compare the guess num and the random num
        if guess == x:
            # send to client win comment And end the connection
            send_to_client(sc, win_comment)
            logger.info('The Client win the Game. End the connection')
            return
        elif guess < x:
            # save down comment to response buffer
            server_response_buffer += down_comment
        elif guess > x:
            # save up comment to response buffer
            server_response_buffer += up_comment

        # check attempt count
        count += 1

    # if client's attempt is over
    if server_response_buffer == '':
        send_to_client(sc, attempt_comment)
    else:
        send_to_client(sc, server_response_buffer + attempt_comment)
    logger.info(attempt_comment)


def make_ssl_socket(sc, certfile, cafile):
    try:
        # make context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.purpose = ssl.Purpose.CLIENT_AUTH
        context.load_cert_chain(certfile=cafile, keyfile=certfile)
        context.load_verify_locations(cafile=cafile)

        # return server's wrapped socket
        return context.wrap_socket(sc, server_side=True)
    except ssl.SSLCertVerificationError as e:
        logger.error("SSL Cert Verification Error: %s", e)
        exit(0)
    except ssl.SSLError as e:
        logger.error("SSL Error: %s", e)
        exit(0)
    except FileNotFoundError as e:
        logger.error("File Not Found Error : %s", e)
        exit(0)
    except Exception as e:
        logger.error("Error : %s", e)
        exit(0)


def make_socket():
    try:
        # use IPv4, TCP protocol
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as e:
        logger.error("Socket Error: %s", e)
        exit(0)
    return s


def bind_socket(s):
    try:
        s.bind(('127.0.0.1', 8080))
    except socket.error as e:
        logger.error("Socket Error: %s", e)
        exit(0)


def listen_socket(s):
    try:
        s.listen(1)
        logger.info("Listening on {}:{}".format(s.getsockname()[0], s.getsockname()[1]))
    except socket.error as e:
        logger.error("Listen Error:", e)
        exit(0)


def accept_socket(s):
    try:
        sc, addr = s.accept()
        # print address of client
        logger.info("Accepted connection from {}:{}".format(addr[0], addr[1]))
    except socket.error as e:
        logger.error("Socket Error: %s", e)
        exit(0)
    return sc


def dump_json(data):
    try:
        # serialize data to json
        serialized_data = json.dumps(data).encode('utf-8')
    except TypeError as e:
        logger.error("Type Error : %s", e)
        exit(0)
    except json.JSONDecodeError as e:
        logger.error("JSON Error : %s", e)
        exit(0)
    return serialized_data


def load_json(data):
    try:
        # deserialize json data
        deserialized_data = json.loads(data.decode('utf-8'))
    except TypeError as e:
        logger.error("Type Error : %s", e)
        exit(0)
    except json.JSONDecodeError as e:
        logger.error("JSON DecodeError : %s", e)
        exit(0)
    return deserialized_data


def invalid_input_error():
    # save invalid input error comment to response buffer
    global server_response_buffer
    logger.info(invalid_input_error_comment)
    server_response_buffer += invalid_input_error_comment


def print_history(history_list):
    for history in history_list:
        # decompress history data
        decompressed_history = zlib.decompress(history).decode('utf-8')
        # print history data in Server's console
        print("-----------------")
        print(decompressed_history)
        print("-----------------")


def load_history():
    try:
        # load history list
        with open('h.pickle', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        # if there is no history file, init history
        init_history()
        return []
    except Exception as e:
        logger.error("Error : %s", e)
        exit(0)


def save_history():
    # load history list
    loaded_history_list = load_history()
    try:
        with open('h.pickle', 'wb') as f:
            # compress history string data
            compressed_history = zlib.compress(history_data.encode('utf-8'))
            # add recent log history
            loaded_history_list.append(compressed_history)
            # save history list
            pickle.dump(loaded_history_list, f)
    except FileNotFoundError:
        # if there is no history file, init history
        init_history()
    except Exception as e:
        logger.error("Error : %s", e)
        exit(0)


def init_history():
    try:
        with open('h.pickle', 'wb') as f:
            pickle.dump([], f)
    except Exception as e:
        logger.error("Error : %s", e)
        exit(0)


def close_socket(s, sc):
    # save messages exchanged in the game
    save_history()
    logger.info("Connection closed")
    # close sockets
    sc.close()
    s.close()


def end_connection(s, sc):
    # send end comment to client
    send_to_client(sc, end_comment)
    logger.info(end_comment)
    # close socket connection
    close_socket(s, sc)
    exit(0)


def save_history_data(data):
    # save history data using history_data string
    global history_data
    history_data += data


def send_to_client(sc, data):
    # send data to client and save data
    sc.sendall(dump_json(data))
    save_history_data(data)


if __name__ == '__main__':
    # set argument for pem file
    parser = argparse.ArgumentParser(description='Server for Number Guess Game')
    parser.add_argument('-a', metavar='cafile', default=None,
                        help='path to CA PEM file')
    parser.add_argument('-s', metavar='certfile', default=None,
                        help='path to server PEM file')
    args = parser.parse_args()

    server(args.s, args.a)
