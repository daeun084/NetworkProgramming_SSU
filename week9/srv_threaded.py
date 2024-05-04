import zen_utils
from threading import Thread


# def create_srv_socket(address):
#     listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     listener.bind(address)
#     listener.listen(64)
#     print('Listening at {}'.format(address))
#     return listener

aphorisms = {b'Beautiful is better than?': b'Ugly.',
             b'Explicit is better than?': b'Implicit.',
             b'Simple is better than?': b'Complex.'}


def get_answer(aphorism):
    # time.sleep(0.0)  # increase to simulate delay
    return aphorisms.get(aphorism, b'Error: unknown aphorism.')


def accept_connections_forever(listener):
    while True:
        sock, address = listener.accept()
        print('Accepted connection from {}'.format(address))
        handle_conversation(sock, address)


def handle_conversation(sock, address):
    try:
        while True:
            handle_request(sock)
    except EOFError:
        print('Client socket to {} has closed'.format(address))
    except Exception as e:
        print('Client {} error: {}'.format(address, e))
    finally:
        sock.close()


def handle_request(sock):
    aphorism = recv_until(sock, b'?')
    answer = get_answer(aphorism)
    sock.sendall(answer)


def recv_until(sock, suffix):
    message = sock.recv(4096)
    if not message:
        raise EOFError('socket closed')
    while not message.endswith(suffix):
        data = sock.recv(4096)
        if not data:
            raise IOError('received {!r} then socket closed'.format(message))
        message += data
    return message


def start_threads(listener, workers=4):
    t = (listener,)
    for i in range(workers):
        th = Thread(target=zen_utils.accept_connections_forever, args=t)
        th.start()


if __name__ == '__main__':
    address = zen_utils.parse_command_line('multi-threaded server')
    listener = zen_utils.create_srv_socket(address)
    start_threads(listener)
