from wsgiref.simple_server import make_server
import webob, time


def app(environ, start_response):
    request = webob.Request(environ)
    if environ['REQUEST_METHOD'] != 'GET':
        response = webob.Response('501 Not Implemented', status=501)
    elif request.domain != '127.0.0.1' or request.path != '/':
        response = webob.Response('404 Not Found', status=404)
    else:
        response = webob.Response(time.ctime())
    return response(environ, start_response)


if __name__ == "__main__":
    httpd = make_server('', 8080, app)
    host, port = httpd.socket.getsockname()
    print('Serving on http://%s:%s' % (host, port))
    httpd.serve_forever()