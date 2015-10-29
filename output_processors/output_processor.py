class OutputProcessor(object):

    def __init__(self):
        self._table = None
        self._delimiter = None

    def setup(self, table, delimiter):
        self._table = table
        self._delimiter = delimiter

    @property
    def height(self):
        raise AssertionError("Not implemented")

    def draw_preview(self, pad):
        raise AssertionError("Not implemented")

    def process(self):
        raise AssertionError("Not implemented")
