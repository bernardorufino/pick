class Selector(object):

    def __init__(self):
        self._table = None
        self._view = None
        self.position = (0, 0)

    def setup(self, table, view):
        self._table = table
        self._view = view

    def move(self, di, dj):
        i, j = self.position
        self.position = (i + di, j + dj)

    def draw(self, pad):
        raise AssertionError("Not implemented")

    def draw_instructions(self, pad):
        pass

    def clear(self, pad):
        pass

    def handle_input(self, c):
        raise AssertionError("Not implemented")
