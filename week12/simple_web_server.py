from wsgiref.simple_server import make_server


def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain; charset=utf-8')]
    # declare status and headers in response
    start_response(status, response_headers)
    # return iterable that yields byte strings
    response = ['Hello World!\n'.encode('utf-8')]
    return response


if __name__ == "__main__":
    # make new WSGI server
    # accept connections for app
    httpd = make_server('', 8080, simple_app)
    host, port = httpd.socket.getsockname()
    print("Serving on %s:%s" % (host, port))
    httpd.serve_forever()

