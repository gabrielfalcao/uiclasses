class AlmostDict(object):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def __setitem__(self, key, value):
        return self.data.__setitem__(key, value)

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    def __iter__(self):
        return self.data.__iter__()

    def next(self):
        return self.data.next()
