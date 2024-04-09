import pickle

class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.area = self.width * self.height

def rect():
    rect = Rectangle(10, 20)
    pickle.dumps(rect)
    pickle_rect(rect)


def pickle_rect(rect):
    with open('rect.data', 'wb') as f:
        pickle.dump(rect, f)

    with open('rect.data', 'rb') as f:
        r = pickle.load(f)

    print("%d x %d" % (r.width, r.height))


if __name__ == '__main__':
    rect()