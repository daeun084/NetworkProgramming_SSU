import argparse
import socket


result = {'query': '', 'country': '', 'regionName': '', 'city': '', 'lat': '', 'lon': ''}


def geocode(address):
    # make socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_ip = 'ip-api.com'
    except socket.error as e:
        print("Socket Error:", e)
        exit(0)

    # connect socket connection
    try:
        s.connect((s_ip, 80))
    except socket.error as e:
        print("Socket Connection Error:", e)
        exit(0)

    # set socket timeout
    s.settimeout(5)

    # make HTTP request
    request_text = 'GET /json/{} HTTP/1.1\r\nHost: ip-api.com\r\nUser-Agent: Daeun\r\nConnection: close\r\n\r\n'
    request = request_text.format(address)

    # send request
    try:
        s.sendall(request.encode('utf-8'))
    except Exception as e:
        # handle exception
        print(f"Failed to send request: {e}")

    # get response
    response = recvall(s)

    # separate header and body
    response_str = response.decode('utf-8')
    header, body = response_str.split('\r\n\r\n', 1)

    # parse body
    parse_result(body)

    # print the result
    print_result()


def recvall(sock):
    response = b''

    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break
            response += data
        except socket.timeout:
            print("Timeout occurred while receiving data")
            break
    return response


def parse_result(body):
    params = body.strip('{}').split(',')
    for param in params:
        # separate dictionary's key, value
        key, value = param.split(':')
        # remove '"'
        key = key.strip('"')
        value = value.strip('"')

        # update the dictionary's values
        if result.keys().__contains__(key):
            result.update({key: value})


def print_result():
    # print the result dictionary
    for key in result:
        print(f'{key} = {result.get(key)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='IP address for IP Geolocation')
    parser.add_argument('address')
    args = parser.parse_args()
    geocode(args.address)
