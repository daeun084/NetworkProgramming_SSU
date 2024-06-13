from urllib.parse import urlsplit, unquote, parse_qsl, urlunsplit, quote, urlencode


def urlparse():
    u = urlsplit('http://example.com/Q%26A/TCP%2FIP?q=packet+loss')
    path = [unquote(s) for s in u.path.split('/')]
    query = parse_qsl(u.query)
    print(path)
    print(query)
    reconstructing_url(path, query)


def reconstructing_url(path, query):
    u = urlunsplit(('http', 'example.com',
                   '/'.join(quote(p, safe=' ') for p in path),
                   urlencode(query), ''))
    print(u)


if __name__ == '__main__':
    urlparse()
