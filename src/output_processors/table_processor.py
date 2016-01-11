import curses
import os
from output_processors.output_processor import OutputProcessor
from table.table import Table
from utils import printstr, join_line


class TableProcessor(OutputProcessor):

    # TODO: Remove deprecated property due to output processor switch feature (we always need the highest height now)
    @property
    def height(self):
        return self._table.height

    @property
    def name(self):
        return "Table output"

    def draw_preview(self, pad):
        # TODO: Create custom method draw_subtable in Table class instead of having to create a new object here
        if self._table.selection:
            pad.move(0, 0)
            output = self._structured_output()
            output_table = Table(output)
            printstr(pad, "Table {}x{} with {} filled cells".format(output_table.height, output_table.ncolumns,
                                                                    len(self._table.selection)),
                     curses.color_pair(7))
            output_table.draw(pad, lambda p, content: 0, margin=(1, 0))

    def process(self):
        output = self._structured_output()
        return os.linesep.join(join_line(line, self._delimiter) for line in output)

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
