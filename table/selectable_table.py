from table import Table


class SelectableTable(Table):

    def __init__(self, input_table):
        super(SelectableTable, self).__init__(input_table)
        # TODO: Use linked (hash) set?
        self.selection = []

    @property
    def selection_content(self):
        return [self.get(p) for p in self.selection]

    def toggle_select(self, p):
        if p in self.selection:
            self.selection.remove(p)
        else:
            self.selection.append(p)

    def clear_selection(self):
        self.selection.clear()

    def select_column(self, j):
        for i, row in enumerate(self.table):
            if j >= len(row):
                continue
            p = (i, j)
            if p not in self.selection:
                self.selection.append(p)

    def _iterate_subtable(self, (ra, ca), (rb, cb), callable):
        for i in range(min(ra, rb), max(ra, rb) + 1):
            row = self.table[i]
            last = len(row) - 1
            for j in range(min(ca, cb), min(max(ca, cb), last) + 1):
                callable((i, j))

    def select_subtable(self, a, b):
        def run(p):
            if p not in self.selection:
                self.selection.append(p)
        self._iterate_subtable(a, b, run)

    def deselect_subtable(self, a, b):
        def run(p):
            if p in self.selection:
                self.selection.remove(p)
        self._iterate_subtable(a, b, run)





