import asyncio, zen_utils


class ZenServer(asyncio.Protocol):
    # called when a client connects to the server
    def connection_made(self, transport):
        # communication channel with the client
        self.transport = transport
        self.address = transport.get_extra_info('peername')
        self.data = b''
        print('Accepted connection from {}'.format(self.address))

    # called when data is received from the client
    def data_received(self, data):
        self.data += data
        if self.data.endswith(b'?'):
            answer = zen_utils.get_answer(self.data)
            # write the answer to the client
            self.transport.write(answer)
            self.data = b''

    # called when the client closes the connection
    def connection_lost(self, error):
        if error:
            print('Client {} Error: {}'.format(self.address, error))
        elif self.data:
            print('Client {} sent {} but then closed'.format(self.address, self.data))
        else:
            print('Client {} closed socket normally'.format(self.address))
        super().connection_lost(error)


if __name__ == '__main__':
    address = zen_utils.parse_command_line('asyncio server using callbacks')
    # get current event loop
    loop = asyncio.get_event_loop()
    # create a server instance
    coro = loop.create_server(ZenServer, *address)
    # run until coro is completed
    server = loop.run_until_complete(coro)
    print('Listening at {}'.format(address))
    try:
        loop.run_forever()
    finally:
        server.close()
        loop.close()