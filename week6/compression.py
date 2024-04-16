import zlib


def compress():
    data = b'AAAAAAAAAAAAAAAAAAAAAAA'
    compressed = zlib.compress(data)
    print(compressed)

    decompressed = zlib.decompress(compressed)
    print(decompressed)


def decompressobj():
    data = zlib.compress(b'Python') + b'.' + zlib.compress(b'zlib') + b'.'
    d = zlib.decompressobj()
    print(d.decompress(data[0:8]), d.unused_data)


if __name__ == '__main__':
    compress()
    decompressobj()