import pickle
from io import BytesIO # import for pickle.load

def pickle_dumps():
    ret = pickle.dumps([5, 6])
    print(ret)
    return ret


def pickle_loads():
    ret = pickle.loads(pickle_dumps())
    print(ret)
    return ret


def pickle_load():
    f = BytesIO(b'\x80\x04\x95\t\x00\x00\x00\x00\x00\x00\x00]\x94(K\x05K\x06e.blahblah')
    print(pickle.load(f)) #[5, 6]
    print(f.read()) #b'blahblah'


if __name__ == '__main__':
    pickle_dumps()
    pickle_loads()
    pickle_load()
