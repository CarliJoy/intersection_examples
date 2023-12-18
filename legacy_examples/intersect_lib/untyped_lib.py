# Here this is assumed to be an external library


class NumberLike:
    def __init__(self, f):
        self.f = f

    def multiplier(self):
        return 2 * self.f


NumberLike: Any
