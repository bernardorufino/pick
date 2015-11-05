class Table(object):

    # table has to be a list of lists
    def __init__(self, input_table):
        self.table = [[cell for cell in row] for row in input_table]
        self._column_widths = self._get_column_widths(self.table)
        self._column_offsets = self._get_column_offsets(self._column_widths)

    @property
    def height(self):
        return len(self.table)

    @property
    def ncolumns(self):
        return len(self._column_widths)

    @property
    def ncells(self):
        return sum(len(row) for row in self.table)

    @property
    def width(self):
        return sum(self._column_widths)

    # TODO: Remove margin and use current position in pad (tried but got errors)
    def draw(self, pad, flags_provider, margin=(0, 0)):
        top, left = margin
        for i, row in enumerate(self.table):
            for j, content in enumerate(row):
                p = (i, j)
                width = self._column_widths[j]
                content = content.ljust(width)
                flags = flags_provider(p, content)
                y = i
                x = self._column_offsets[j]
                pad.addstr(top + y, left + x, content, flags)

    def get(self, (i, j)):
        return self.table[i][j]

    def column_width(self, j):
        return self._column_widths[j]

    def column_offset(self, j):
        return self._column_offsets[j]

    @staticmethod
    def _get_column_widths(table):
        widths = []
        for row in table:
            for j, cell in enumerate(row):
                w = len(cell)
                if j < len(widths):
                    widths[j] = max(widths[j], w)
                else:
                    assert j == len(widths)
                    widths.append(w)
        return [w + 2 for w in widths]

    @staticmethod
    def _get_column_offsets(widths):
        n = len(widths)
        offsets = [0] * (n + 1)
        for i in xrange(1, n + 1):
            offsets[i] = offsets[i - 1] + widths[i - 1]
        return offsets

