import curses

from selectors.selector import Selector


class SingleSelector(Selector):

    def __init__(self):
        super(SingleSelector, self).__init__()
        self._selection = None

    def draw(self, pad):
        self._selection = set(self._table.selection)
        self._table.draw(pad, self._flags_for)

    def _flags_for(self, p, content):
        flags = 0
        if p == self.position:
            flags |= curses.color_pair(2)
        elif p in self._selection:
            flags |= curses.A_REVERSE
        else:
            flags |= curses.color_pair(1)
        return flags

    def handle_input(self, c):
        redraw_output = False
        if c == ord(' '):
            self._table.toggle_select(self.position)
            redraw_output = True
        elif c == ord('d'):
            self._table.clear_selection()
            redraw_output = True
        elif c == ord('c'):
            self._table.select_column()
            redraw_output = True
        return redraw_output



