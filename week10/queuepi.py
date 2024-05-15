import random
import threading
import time
import zmq

B = 32


def bitsource(zcontext, url):
    # publisher
    zsock = zcontext.socket(zmq.PUB)
    zsock.bind(url)
    while True:
        # produce string consisting of ones and zeros
        # send data to subscribers as always_yes, judge
        zsock.send_string(ones_and_zeros(B * 2))
        time.sleep(0.01)


def ones_and_zeros(digits):
    return bin(random.getrandbits(digits)).lstrip('0b').zfill(digits)


def always_yes(zcontext, in_url, out_url):
    # subscriber
    isock = zcontext.socket(zmq.SUB)
    # connect to bitsource
    isock.connect(in_url)
    # only receive strings starting with 00
    isock.setsockopt(zmq.SUBSCRIBE, b'00')

    # connect with tally
    osock = zcontext.socket(zmq.PUSH)
    osock.connect(out_url)
    while True:
        isock.recv_string()
        # push Y to tally
        osock.send_string('Y')


def judge(zcontext, in_url, pythagoras_url, out_url):
    # subscriber
    isock = zcontext.socket(zmq.SUB)
    # connect to bitsource
    isock.connect(in_url)
    # receive strings as 01, 10, 11
    for prefix in b'01', b'10', b'11':
        isock.setsockopt(zmq.SUBSCRIBE, prefix)

    # connect with pythagoras
    psock = zcontext.socket(zmq.REQ)
    psock.connect(pythagoras_url)

    # connect with tally
    osock = zcontext.socket(zmq.PUSH)
    osock.connect(out_url)

    unit = 2 ** (B * 2)
    while True:
        bits = isock.recv_string()
        n, m = int(bits[::2], 2), int(bits[1::2], 2)
        # send and receive data with json format
        psock.send_json((n, m))
        sumsquares = psock.recv_json()
        osock.send_string('Y' if sumsquares < unit else 'N')


def pythagoras(zcontext, url):
    # bind with judge
    zsock = zcontext.socket(zmq.REP)
    zsock.bind(url)
    while True:
        # send and receive data with json format
        numbers = zsock.recv_json()
        zsock.send_json(sum(n * n for n in numbers))


def tally(zcontext, url):
    zsock = zcontext.socket(zmq.PULL)
    zsock.bind(url)
    p = q = 0
    while True:
        decision = zsock.recv_string()
        q += 1
        if decision == 'Y':
            p += 4
        print(decision, p, q, p / q)


def start_thread(function, *args):
    thread = threading.Thread(target=function, args=args)
    # easily copy the whole program
    thread.daemon = True
    thread.start()


def main(zcontext):
    # set url
    pubsub = 'tcp://127.0.0.1:6700'
    reqrep = 'tcp://127.0.0.1:6701'
    pushpull = 'tcp://127.0.0.1:6702'

    # each thread create its own socket for communication
    start_thread(bitsource, zcontext, pubsub)
    start_thread(always_yes, zcontext, pubsub, pushpull)
    start_thread(judge, zcontext, pubsub, reqrep, pushpull)
    start_thread(pythagoras, zcontext, reqrep)
    start_thread(tally, zcontext, pushpull)


if __name__ == "__main__":
    # the threads share a single context obj
    # create only one context per process
    main(zmq.Context())
