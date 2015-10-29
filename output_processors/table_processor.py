import os
from output_processors.output_processor import OutputProcessor
from table.table import Table


class TableProcessor(OutputProcessor):

    @property
    def height(self):
        return self._table.height

    def draw_preview(self, pad):
        # TODO: Create custom method draw_subtable in Table class instead of having to create a new object here
        output = self._structured_output()
        return Table(output).draw(pad, lambda p, content: 0)

    def process(self):
        output = self._structured_output()
        return os.linesep.join(self._delimiter.join(line) for line in output)

    def _structured_output(self):
        # TODO: Add option to compress column widths?
        selection = sorted(self._table.selection)
        selection_set = set(selection)
        cols = set()
        rows = set()
        for (i, j) in selection:
            rows.add(i)
            cols.add(j)
        output = []
        for i in sorted(rows):
            line = []
            for j in sorted(cols):
                p = (i, j)
                width = self._table.column_width(j)
                content = self._table.get(p) if p in selection_set else ''
                content = content.ljust(width)
                line.append(content)
            output.append(line)
        return output
