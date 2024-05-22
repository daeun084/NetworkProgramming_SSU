import socket
import json
import ssl
import argparse
import logging

win_comment = 'Congratulations, you did it.\n'
end_comment = "User don't start Game! End the Connection\n"
attempt_comment = "Sorry, you've used all your attempts!\n"

MAX_BYTES = 1024 * 1024
logger = logging.getLogger('client')


def client(cafile=None):
    # make socket
    s = make_socket()

    # set timeout to udp socket
    s.settimeout(5)

    # connect socket
    connect_socket(s)

    # make socket with ssl
    s = make_ssl_socket(s, cafile)

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
        print(response)

        # check the response message
        if check_comment(response):
            break

        # accept the input for request and guess num
        send_request(s)

    # close socket connection
    close_socket(s)


def make_ssl_socket(s, cafile):
    try:
        # make context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.purpose = ssl.Purpose.SERVER_AUTH
        context.load_verify_locations(cafile)

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
    # accept the input for request and guess num
    deserialized_request = input()
    # send the serialized request message to server
    request = dump_json(deserialized_request)
    s.sendall(request)


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
    # set argument for pem file
    parser = argparse.ArgumentParser(description='Client for Number Guess Game')
    parser.add_argument('-a', metavar='cafile', default=None,
                        help='path to CA PEM file')
    args = parser.parse_args()

    client(args.a)
