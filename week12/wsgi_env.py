from pprint import pformat
from wsgiref.simple_server import make_server


def simple_app(environ, start_response):
    status = '200 OK'
    headers = {'Content-type': 'text/plain; charset=utf-8'}
    # declare status and headers in response
    start_response(status, list(headers.items()))
    yield 'Here is the WSGI environment:\r\n\r\n'.encode('utf-8')
    yield pformat(environ).encode('utf-8')


if __name__ == "__main__":
    # make new WSGI server
    # accept connections for app
    httpd = make_server('', 8080, simple_app)
    host, port = httpd.socket.getsockname()
    print("Serving on %s:%s" % (host, port))
    httpd.serve_forever()

