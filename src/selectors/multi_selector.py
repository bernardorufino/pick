import curses
from vendor.enum import Enum
from selector import Selector
from utils import printstr


class MultiSelector(Selector):

    class State(Enum):
        move = 0
        select = 1
        deselect = 2

    ACTIVE_STATES = [State.select, State.deselect]

    def __init__(self):
        super(MultiSelector, self).__init__()
        self._initial_position = None
        self._selection = None
        self._state = self.State.move

    def draw(self, pad):
        self._selection = set(self._table.selection)
        self._table.draw(pad, self._flags_for)

    def _flags_for(self, p, content):
        flags = 0
        if p == self.position:
            flags |= curses.color_pair(2)
        elif self._state in self.ACTIVE_STATES and self._in_current_subtable(p):
            if self._state == self.State.select:
                flags |= curses.A_REVERSE
            else:
                assert self._state == self.State.deselect
                flags |= curses.color_pair(1)
        elif p in self._selection:
            flags |= curses.A_REVERSE
        else:
            flags |= curses.color_pair(1)
        return flags

    def _in_current_subtable(self, p):
        i1, j1 = self._initial_position
        i2, j2 = self.position
        i, j = p
        return min(i1, i2) <= i <= max(i1, i2) and min(j1, j2) <= j <= max(j1, j2)

    def handle_input(self, c):
        redraw_output = False
        if self._state == self.State.move:
            if c == ord(' '):
                self._initial_position = self.position
                redraw_output = True
                self._state = self.State.select
            elif c == ord('d'):
                self._initial_position = self.position
                redraw_output = True
                self._state = self.State.deselect
        elif self._state == self.State.select:
            if c == ord(' '):
                self._table.select_subtable(self._initial_position, self.position)
                redraw_output = True
                self._state = self.State.move
        elif self._state == self.State.deselect:
            if c == ord(' ') or c == ord('d'):
                self._table.deselect_subtable(self._initial_position, self.position)
                redraw_output = True
                self._state = self.State.move
        return redraw_output

    def draw_instructions(self, pad):
        # TODO: Remove hard-coded dependency on next selector, see View class for details
        printstr(pad, "Multi-selection", curses.color_pair(7))
        printstr(pad, "     [i] single-selection                                                     ", curses.color_pair(3))
        printstr(pad, "[arrows] move                               [d] start/end subtable deselection", curses.color_pair(3))
        printstr(pad, " [space] start/end subtable selection   [enter] print and copy                ", curses.color_pair(3))
        printstr(pad, "     [p] print current                      [q] abort                         ", curses.color_pair(3))
        printstr(pad)
