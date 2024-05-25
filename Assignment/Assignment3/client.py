import asyncio
import socket, json, ssl, argparse, logging, zmq
import zmq.asyncio

win_comment = 'Congratulations, you did it.\n'
end_comment = "User want to exit Game! End the Connection\n"
attempt_comment = "Sorry, you've used all your attempts!\n"
start_comment = "Choose the GAME MODE"

MAX_BYTES = 1024 * 1024

# set logger
logger = logging.getLogger('client')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
logger.addHandler(console)

multi_flag = 0

SSL_CAFILE = None


def client():
    # make socket
    s = make_socket()

    # set timeout to socket
    s.settimeout(60)

    # connect socket
    connect_socket(s)

    # make socket with ssl
    s = make_ssl_socket(s)

    # get response
    while True:
        try:
            deserialized_response = s.recv(MAX_BYTES)
            response = load_json(deserialized_response)

        except socket.timeout as e:
            # catch timeout error
            logger.error("Timeout occured while receiving data : %s", e)
            break
        except ConnectionResetError as e:
            # catch reset error
            logger.error("Connection with server reset : %s", e)
            break

        # print the response message to client
        logger.info("%s", response)

        # check the response message
        if check_comment(response):
            break

        # accept the input for request and guess num
        send_request(s)

    # close socket connection
    close_socket(s)


def make_ssl_socket(s):
    global SSL_CAFILE
    try:
        # make context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.purpose = ssl.Purpose.SERVER_AUTH
        context.load_verify_locations(SSL_CAFILE)

        # return client's wrapped socket
        return context.wrap_socket(s, server_hostname='daeun kim')
    except ssl.SSLCertVerificationError as e:
        logger.error("SSL Certificate verification Error : %s", e)
        exit(0)
    except ssl.SSLError as e:
        logger.error("SSL Error : %s", e)
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
    except socket.error as e:
        logger.error("Socket Error : %s", e)
        exit(0)
    return s


def connect_socket(s):
    try:
        s.connect(('127.0.0.1', 8080))
        logger.info("Connected to {}:{}".format(s.getsockname()[0], s.getsockname()[1]))
    except socket.error as e:
        logger.error("Socket Error : %s", e)
        exit(0)


def send_request(s):
    global multi_flag

    # accept the input for request and guess num
    deserialized_request = input()
    request = dump_json(deserialized_request)

    # send the serialized request message to server
    s.sendall(request)
    if deserialized_request.strip().__eq__("2") and multi_flag == 1:
        asyncio.run(multi_mode())
    multi_flag = 0


async def receive_server_message(ssock):
    # monitoring PUB's MESSAGE
    while True:
        try:
            response = await ssock.recv()
            response = load_json(response)
            logger.info("[* PUB] %s", response)

        except Exception as e:
            logger.error("Exception : %s", e)
            break


async def communicate_with_server(rsock):
    # send data to server for giving client's identity
    await rsock.send(dump_json("Enter the Multiple Game"))

    while True:
        # communication with server using DEALER-ROUTER
        try:
            # recv message from server
            await asyncio.sleep(0.01)
            response = await rsock.recv()
            response = load_json(response)
            logger.info(response)

            # 'exit' 메시지를 받으면 종료
            if response == "exit":
                return

            await asyncio.sleep(0.01)

            # send message to server
            request = dump_json(input())
            await rsock.send(request)
            await asyncio.sleep(0.01)

        except ConnectionResetError as e:
            logger.error("Connection Reset : %s", e)
            break


async def multi_mode():
    logger.info("Start the Number Guess in Multi Mode")

    # make subscriber
    ssock = zmq.asyncio.Context().socket(zmq.SUB)
    ssock.setsockopt(zmq.SUBSCRIBE, b"")
    ssock.connect('tcp://127.0.0.1:8081')
    # ssock = make_ssl_socket(ssock)

    # make dealer
    rsock = zmq.asyncio.Context().socket(zmq.DEALER)
    rsock.connect('tcp://127.0.0.1:8082')
    # rsock = make_ssl_socket(rsock)

    # run codes
    task1 = asyncio.create_task(communicate_with_server(rsock))
    task2 = asyncio.create_task(receive_server_message(ssock))
    # if task1 or task2 end, terminate the other method
    await asyncio.wait([task1, task2], return_when=asyncio.FIRST_COMPLETED)

    # end multi mode close sockets
    ssock.close()
    rsock.close()
    logger.info("Close Game in Multi Mode")


def dump_json(data):
    try:
        # serialize the data
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
        # deserialize the data
        deserialized_data = json.loads(data.decode('utf-8'))
    except TypeError as e:
        logger.error("Type Error : %s", e)
        exit(0)
    except json.JSONDecodeError as e:
        logger.error("JSON Error : %s", e)
        exit(0)
    return deserialized_data


def close_socket(s):
    # close the socket
    logger.info("Closing socket")
    s.shutdown(socket.SHUT_WR)
    s.close()


def check_comment(response):
    # case for client don't start the game
    if response.__eq__(end_comment):
        return True
    if start_comment in response:
        global multi_flag
        multi_flag = 1
    else:
        return False


def set_ssl_certificate(args):
    global SSL_CAFILE
    SSL_CAFILE = args.a


def parse_command():
    # set argument for pem file
    parser = argparse.ArgumentParser(description='Client for Number Guess Game')
    parser.add_argument('-a', metavar='cafile', default=None,
                        help='path to CA PEM file')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_command()
    set_ssl_certificate(args)
    client()
