import curses
import os
from output_processors.output_processor import OutputProcessor
from utils import printstr, writestr


class ListProcessor(OutputProcessor):

    @property
    def height(self):
        return self._table.ncells

    @property
    def name(self):
        return "List output"

    def draw_preview(self, pad):
        if self._table.selection:
            pad.move(0, 0)
            printstr(pad, "[{}] cells selected".format(len(self._table.selection)), curses.color_pair(7))
            for content in self._table.selection_content:
                i, j = pad.getyx()
                writestr(pad, " |=> ", curses.color_pair(1))
                printstr(pad, content, curses.color_pair(1))
                pad.move(i + 1, j)
    
    def process(self):
        return os.linesep.join(self._table.selection_content)
