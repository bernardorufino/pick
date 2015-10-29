from utils import limit


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
        i = limit(i + di, 0, self._table.height - 1)
        j = limit(j + dj, 0, len(self._table.table[i]) - 1)
        self.position = (i, j)

    def draw(self, pad):
        raise AssertionError("Not implemented")

    def draw_instructions(self, pad):
        pass

    def clear(self, pad):
        pass

    def handle_input(self, c):
        raise AssertionError("Not implemented")
