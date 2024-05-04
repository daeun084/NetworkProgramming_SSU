import zen_utils, select


def all_events_forever(poll_object):
    while True:
        for fd, event in poll_object.poll():
            yield fd, event


def serve(listener):
    # dictionary mapping file descriptors to socket objects
    sockets = {listener.fileno(): listener}
    addresses = {}

    # buffer for data to wait until the next turn in polling
    # important functionally for async server
    bytes_received = {}
    bytes_to_send = {}

    # create poll object and register listener socket
    poll_object = select.poll()
    # POOLIN: there is data to read
    poll_object.register(listener, select.POLLIN)

    for fd, event in all_events_forever(poll_object):
        sock = sockets[fd]

        # Case 1 : Socket closed
        # remove it from out data structure
        if event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
            address = addresses.pop(sock)

            # check contents in the buffers
            # see if there is any message
            rb = bytes_received.pop(sock, b'')
            sb = bytes_to_send.pop(sock, b'')
            if rb:
                print('Client {} sent {} but then closed'.format(address, rb))
            elif sb:
                print('Client {} closed before we sent {}'.format(address, sb))
            else:
                print('Client {} closed socket normally'.format(address))
            poll_object.unregister(fd)
            del sockets[fd]

        # Case 2 : New Socket
        # add it to out data structure
        elif sock is listener:
            sock, address = sock.accept()
            print('Accepted connection from {}'.format(address))
            sock.setblocking(False)
            sockets[sock.fileno()] = sock
            addresses[sock] = address
            poll_object.register(sock, select.POLLIN)

        # Case 3 : Incoming data
        # keep receiving data until we see the suffix
        elif event & select.POLLIN:
            more_data = sock.recv(4096)
            if not more_data:  # EOF
                sock.close()  # next poll() will POLLNVAL, and thus clean up
                continue
            data = bytes_received.pop(sock, b'') + more_data
            if data.endswith(b'?'):
                bytes_to_send[sock] = zen_utils.get_answer(data)
                poll_object.modify(sock, select.POLLOUT)
            else:
                bytes_received[sock] = data

        # Case 4 : Socket ready to send data
        # keep sending data until all bytes are delivered
        elif event & select.POLLOUT:
            # get data from send buffer of the socket
            data = bytes_to_send.pop(sock)
            n = sock.send(data)
            if n < len(data):
                bytes_to_send[sock] = data[n:]
            else:
                poll_object.modify(sock, select.POLLIN)


if __name__ == '__main__':
    address = zen_utils.parse_command_line('low-level async server')
    listener = zen_utils.create_srv_socket(address)
    serve(listener)