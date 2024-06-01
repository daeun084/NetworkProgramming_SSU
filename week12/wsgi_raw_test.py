import argparse

import requests


def display(r):
    print((r.status_code, r.headers['Content-Type'], r.text))


def t1():
    r1 = requests.get('http://127.0.0.1:8080/')
    display(r1)
    assert r1.status_code == 200


def t2():
    r2 = requests.post('http://127.0.0.1:8080/')
    display(r2)
    assert r2.status_code == 501


def t3():
    r3 = requests.get('http://localhost:8080/')
    display(r3)
    assert r3.status_code == 404


def t4():
    r4 = requests.get('http://127.0.0.1:8080/foo')
    display(r4)
    assert r4.status_code == 404


def t5():
    r5 = requests.get('http://127.0.0.1:8080/')
    display(r5)
    assert r5.status_code == 200


def t6():
    r6 = requests.get('http://127.0.0.1:8080/?abc=123')
    display(r6)
    assert r6.status_code == 200


if __name__ == "__main__":
    t1()
    t2()
    t3()
    t4()
    t5()
    t6()
