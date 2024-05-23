import random, socket, json, ssl, argparse, logging, zmq
import time
from threading import Thread


# comment for client
win_comment = 'Congratulations, you did it.\n'
up_comment = 'Hint: You Guessed too high!\n'
down_comment = 'Hint: You guessed too small!\n'
start_comment = 'Guess the Number! Choose the GAME MODE\n - SingleMode : 1\n - MultiMode : 2\n - Terminate : exit\n'
end_comment = "User want to exit Game! End the Connection\n"
attempt_comment = "Sorry, you've used all your attempts!\n"
guess_comment = '[Guess the number]: '
inform_comment = 'You can attempt to guess the random number (1~10) in 5 chance. if you stop the game, send me "exit".\n[Guess the number]:  '
invalid_input_error_comment = 'Invalid Guess Num. Try again\n'
server_start_buffer = ''
server_response_buffer = ''

MAX_BYTES = 1024 * 1024

# set logger
logger = logging.getLogger('server')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
logger.addHandler(console)

# make publisher
zcontext = zmq.Context()
zsock = zcontext.socket(zmq.PUB)
zsock.bind("tcp://127.0.0.1:8081")

# make router
rsock = zcontext.socket(zmq.ROUTER)
rsock.bind("tcp://127.0.0.1:8082")


def server(sc):
    while True:
        global server_start_buffer

        # inform client about choosing game mode
        send_to_client(sc, server_start_buffer + start_comment)
        server_start_buffer = ''

        try:
            deserialized_start_request = sc.recv(MAX_BYTES)
            start_request = load_json(deserialized_start_request)

            if start_request == 'exit':
                # exit game
                break
            elif start_request == '1':
                # start single mode
                guess_number_game_single_mode(sc)
            elif start_request == '2':
                # start multiple mode
                guess_number_game_multi_mode(sc)
            else:
                # if client doesn't choose game mode, end the connection
                logger.info("Invalid Client's Response")
                end_connection(sc)
        except socket.error as e:
            logger.error("Socket Error while receiving message: %s", e)

    # close socket connection
    end_connection(sc)


def guess_number_game_single_mode(sc):
    global server_start_buffer
    global server_response_buffer
    logger.info("Start the Number Guess Game in Single Mode")

    # count for client's attempt
    count = 0

    # make random number
    x = random.randint(1, 10)

    # client attempt 5 under
    while count < 5:
        # send client for guess the number question
        # use response buffer for send multiple comments
        if count == 0:
            send_to_client(sc, inform_comment)
        else:
            send_to_client(sc, server_response_buffer + guess_comment)

        # after sending buffer's message, init response buffer
        server_response_buffer = ''

        # recv from client the guess number And parse it to int
        try:
            response = sc.recv(MAX_BYTES)
            response = load_json(response)
            if response == 'exit':
                # return to server()
                return
            guess = int(response)
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
            server_start_buffer += win_comment
            logger.info('The Client win the Game.')
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
    server_start_buffer += server_response_buffer + attempt_comment
    logger.info(attempt_comment)


def guess_number_game_multi_mode(sc):
    logger.info("Start the Number Guess Game in Multi Mode")
    global zsock
    global rsock

    # get identity of client
    identity, request = rsock.recv_multipart()

    zsock.send(dump_json("PUB:TEST"))

    for i in range(2):
        print(i)
        rsock.send_multipart([identity, dump_json(inform_comment)])

    rsock.send_multipart([identity, dump_json("bye")])



def create_srv_socket():
    # make socket
    s = make_socket()

    # bind socket
    bind_socket(s)

    # listen socket
    listen_socket(s)
    return s


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

def end_connection(sc):
    # send end comment to client
    send_to_client(sc, end_comment)
    logger.info(end_comment)

    # save messages exchanged in the game
    logger.info("Connection closed")
    # close sockets
    # sc.shutdown(socket.SHUT_RDWR)
    sc.close()
    exit(0)


def send_to_client(sc, data):
    # send data to client and save data
    sc.sendall(dump_json(data))


def send_to_zmq_client(sc, data):
    sc.send(dump_json(data))


def accept_connection_forever(listener, certfile, cafile=None):
    while True:
        # accept client socket
        sc = accept_socket(listener)

        # make socket with ssl
        sc = make_ssl_socket(sc, certfile, cafile)

        server(sc)


def start_threads(listener, certfile, cafile=None):
    # handle 50 client
    for i in range(50):
        th = Thread(target=accept_connection_forever, args=(listener, certfile, cafile))
        th.start()


def parse_command():
    # set argument for pem file
    parser = argparse.ArgumentParser(description='Server for Number Guess Game')
    parser.add_argument('-a', metavar='cafile', default=None,
                        help='path to CA PEM file')
    parser.add_argument('-s', metavar='certfile', default=None,
                        help='path to server PEM file')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_command()
    listener = create_srv_socket()
    start_threads(listener, args.s, args.a)

