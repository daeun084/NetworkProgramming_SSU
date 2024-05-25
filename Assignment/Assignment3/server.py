import random, socket, json, ssl, argparse, logging, zmq, zmq.asyncio
import threading
from threading import Thread
import errno
# import memcache


# comment for client
win_comment = 'Congratulations, you did it.\n'
up_comment = 'Hint: You Guessed too high!\n'
down_comment = 'Hint: You guessed too small!\n'
start_comment = 'Guess the Number! Choose the GAME MODE\n - SingleMode : 1\n - MultiMode : 2\n - Terminate : exit\n'
end_comment = "User want to exit Game! End the Connection\n"
attempt_comment = "Sorry, you've used all your attempts!\n"
guess_comment = '[Guess the number]: '
inform_comment = ('-------\nYou can attempt to guess the random number (1~10) in 5 chance. If you stop the game, '
                  'send me "exit".\n-------\n[Guess the number]:')
restart_comment = ('[* MultiMode] The Stage Is Reset. The Number and Your Attemps for game are reset.\nRestart the '
                   'Game!\n[Guess the number]:')
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

# dictionary for saving client's attempts
dealer_sockets = {}

# random number in multi mode
x = -1
x_lock = threading.Lock()

# ssl
SSL_CERT = None
SSL_CAFILE = ''


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
                guess_number_game_multi_mode()
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
    logger.info("--Start the Number Guess Game in Single Mode--")

    # count for client's attempt
    count = 0

    # make random number
    x = random.randint(1, 10)
    logger.info("[* Singlemode] New Random Number : %s", x)

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
        except ValueError:
            invalid_input_error()
            count += 1
            continue

        # log guess number from client
        logger.info("[Client's Guess Number]: %s", guess)

        # compare the guess num and the random num
        if guess == x:
            # send to client win comment And end the connection
            server_start_buffer += win_comment
            logger.info('[* SingleMode] The Client win the Game.')
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


def guess_number_game_multi_mode():
    logger.info("--Start the Number Guess Game in Multi Mode--")
    global zsock
    global rsock
    global x
    global dealer_sockets
    buff = ''

    # wrap sockets
    # make_ssl_zmq_socket(zsock)
    # make_ssl_zmq_socket(rsock)

    # init random number in once in server's program
    if x == -1:
        with x_lock:
            init_random_num()

    # get identity of client
    identity, request = rsock.recv_multipart()

    # save identity, count
    dealer_sockets[identity] = 0

    # client = memcache.Client(['127.0.0.1:8082'])
    # client.set(identity, 0)

    # send client inform comment
    rsock.send_multipart([identity, dump_json(inform_comment)])

    while True:
        dealer_sockets[identity] = 0

        # client attempt 5 under
        while dealer_sockets[identity] < 5:
            identity = 0
            # send client for guess the number question
            # use response buffer for send multiple comments

            # recv from client the guess number And parse it to int
            try:
                i, response = rsock.recv_multipart()
                # keep client's inform
                identity = i
                response = load_json(response)

                if i not in dealer_sockets:
                    dealer_sockets[i] = 0

                if response == 'exit':
                    # return to server()
                    rsock.send_multipart([i, dump_json('exit')])
                    dealer_sockets.pop(i)
                    return
                guess = int(response)
            except ValueError:
                logger.error('[Value Error] Invalid response')
                rsock.send_multipart([identity, dump_json(invalid_input_error_comment + guess_comment)])
                dealer_sockets[identity] += 1
                continue
            except TypeError:
                logger.error('[Type Error] Invalid response')
                rsock.send_multipart([identity, dump_json(invalid_input_error_comment + guess_comment)])
                dealer_sockets[identity] += 1
                continue

            # check attempt count
            dealer_sockets[identity] += 1

            # log guess number from client
            logger.info("[* MultiMode] [Client's Guess Number]: %s",  guess)

            # compare the guess num and the random num
            with x_lock:
                if guess == x:
                    # send to client win comment
                    logger.info('[* MultiMode] The Client win the Game.')
                    # send message to client
                    rsock.send_multipart([i, dump_json('')])
                    zsock.send(dump_json(win_comment + restart_comment))
                    # save win count
                    # client.incr(i, 1)
                    break
                elif dealer_sockets[identity] == 5:
                    # send message to client
                    rsock.send_multipart([i, dump_json('')])
                    zsock.send(dump_json(attempt_comment + restart_comment))
                    break
                elif guess < x:
                    # save down comment to response buffer
                    buff += down_comment
                elif guess > x:
                    # save up comment to response buffer
                    buff += up_comment

            # send guess message
            rsock.send_multipart([i, dump_json(buff + guess_comment)])
            buff = ''

        # set new game stage
        init_multi_game_stage()


def init_random_num():
    global x
    x = random.randint(1, 10)
    logger.info("[* Multimode] New Random Number : %s", x)


def init_multi_game_stage():
    global dealer_sockets
    logger.info("[* MultiMode] The Stage is RESET .....")
    init_random_num()
    # init all client's attempt
    for i in dealer_sockets:
        dealer_sockets[i] = 0


def create_srv_socket():
    # make socket
    s = make_socket()

    # bind socket
    bind_socket(s)

    # listen socket
    listen_socket(s)
    return s


# def make_ssl_zmq_socket(sc):
#     global SSL_CERT
#     global SSL_CAFILE
#
#     sc.setsockopt(zmq.CURVE_SERVER, 1)
#     # sc.setsockopt(zmq.CURVE_SECRETKEY, SSL_C)
#     sc.setsockopt_string(zmq.CURVE_PUBLICKEY, SSL_CAFILE)
#     sc.setsockopt_string(zmq.CURVE_SERVERKEY, SSL_CERT)


def make_ssl_socket(sc):
    global SSL_CERT
    global SSL_CAFILE

    try:
        # make context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.purpose = ssl.Purpose.CLIENT_AUTH
        context.load_cert_chain(certfile=SSL_CAFILE, keyfile=SSL_CERT)
        context.load_verify_locations(cafile=SSL_CAFILE)

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
    sc.shutdown(socket.SHUT_RDWR)
    sc.close()
    exit(0)


def send_to_client(sc, data):
    # send data to client and save data
    sc.sendall(dump_json(data))


def accept_connection_forever(listener):
    while True:
        # accept client socket
        sc = accept_socket(listener)

        # make socket with ssl
        sc = make_ssl_socket(sc)

        server(sc)


def start_threads(listener):
    # handle 50 client
    for i in range(50):
        th = Thread(target=accept_connection_forever, args=(listener, ))
        th.start()


def set_ssl_certificate(args):
    global SSL_CERT
    global SSL_CAFILE
    SSL_CERT = args.s
    SSL_CAFILE = args.a


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
    set_ssl_certificate(args)
    listener = create_srv_socket()
    start_threads(listener)
