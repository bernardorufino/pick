import curses
from utils import printstr


class View(object):

    DIRECTIONS = {
        curses.KEY_UP: (-1, 0),
        curses.KEY_RIGHT: (0, 1),
        curses.KEY_DOWN: (1, 0),
        curses.KEY_LEFT: (0, -1),
    }
    MARGIN = (1, 2)

    def __init__(self, table, selectors, output_processors, delimiter):
        self._table = table
        self.delimiter = delimiter
        self.table_offset = (0, 0)

        self._selectors = selectors[:]
        self._set_selector(0)

        self._output_processors = output_processors[:]
        self._set_output_processor(0)

        # To be assigned when run is called by curses
        self.screen = None
        self.table_pad = None
        self.output_pad = None

    def _set_selector(self, i):
        old_position = self._selector.position if hasattr(self, '_selector') else (0, 0)
        self._selector = self._selectors[i]
        self._selector.setup(self._table, self)
        self._selector.position = old_position
        
    def _set_output_processor(self, i):
        self._output_processor = self._output_processors[i]
        self._output_processor.setup(self._table, self.delimiter)

    def _setup_curses(self, screen):
        curses.curs_set(0)
        curses.init_pair(1, 251, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, 237, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(7, 240, curses.COLOR_BLACK)

        self.screen = screen
        self.table_pad = curses.newpad(self._table.height + 1, self._table.width)
        # Have to account for header size (width and height)
        # TODO: Remove hard-coded 50 value
        self.output_pad = curses.newpad(self._table.ncells + 2, max(self._table.width, 50))

    def run(self, screen):
        self._setup_curses(screen)

        self.draw(resizing=False, redraw_output=True)
        while True:
            c = self.screen.getch()
            redraw_output = False
            if c == ord('q'):
                return
            elif c == ord('i'):
                i = self._selectors.index(self._selector)
                i = (i + 1) % len(self._selectors)
                self._set_selector(i)
            elif c == ord('o'):
                # TODO: Support switch from table to list with different orientations (row-first or column-first)
                i = self._next_output_processor_index()
                self._set_output_processor(i)
                redraw_output = True
            elif c == ord('p'):
                return self._table.get(self._selector.position)
            elif c in self.DIRECTIONS:
                di, dj = self.DIRECTIONS[c]
                self._selector.move(di, dj)
            elif self.is_enter(c):
                return self._output_processor.process()
            else:
                # TODO: Revisit selector precedence over input handling (mainly capture <enter>)
                redraw_output = self._selector.handle_input(c)
            resizing = (c == -1)
            self.draw(resizing=resizing, redraw_output=redraw_output)

    def _next_output_processor_index(self):
        i = self._output_processors.index(self._output_processor)
        i = (i + 1) % len(self._output_processors)
        return i

    def draw(self, resizing, redraw_output):

        # Compute table_pad dimensions
        top_margin, left_margin = self.MARGIN
        mi, mj = self.screen.getmaxyx()
        table_pad_height = mi / 2 - top_margin
        table_pad_width = mj - left_margin

        # Clear all pads and windows
        self.screen.clear()
        self._selector.clear(self.table_pad)
        if redraw_output:
            self.output_pad.clear()

        # Draw table
        self._selector.draw(self.table_pad)

        # Scroll up/down
        top_offset, left_offset = self.table_offset
        i, j = self._selector.position
        if i > top_offset + table_pad_height - 1:
            top_offset += 1
        elif i < top_offset:
            top_offset -= 1

        # Scroll left/right
        # There's no guarantee that shifting the table one column to the right will make the entire column of the
        # current position visible bc unlike rows columns can have variable width. So, we shift until the column is
        # fully visible.
        shift_left = lambda left: self._table.column_offset(j + 1) > self._table.column_offset(left) + table_pad_width - 1
        if shift_left(left_offset):
            while shift_left(left_offset):
                left_offset += 1
        elif resizing:
            while left_offset >= 1 and self._table.column_offset(j + 1) - self._table.column_offset(left_offset - 1) < table_pad_width:
                left_offset -= 1
        if j < left_offset:
            left_offset -= 1

        # Set h/v scroll
        self.table_offset = (top_offset, left_offset)

        # Draw instructions
        self.screen.move(top_margin + table_pad_height + 1, left_margin)
        h1, _ = self.screen.getyx()
        self._selector.draw_instructions(self.screen)
        printstr(self.screen, self._output_processor.name, curses.color_pair(7))
        next_output_processor = self._output_processors[self._next_output_processor_index()]
        printstr(self.screen, "     [o] {} mode".format(next_output_processor.name), curses.color_pair(3))
        printstr(self.screen)
        h2, _ = self.screen.getyx()
        instructions_h = h2 - h1

        # Output preview
        self._output_processor.draw_preview(self.output_pad)

        # Refresh
        self.screen.noutrefresh()
        self.table_pad.noutrefresh(top_offset, self._table.column_offset(left_offset), top_margin, left_margin,
                                   top_margin + table_pad_height - 1, left_margin + table_pad_width - 1)
        self.output_pad.noutrefresh(0, 0, top_margin + table_pad_height + instructions_h + 1, left_margin, mi - 1, mj - 1)
        curses.doupdate()

    @staticmethod
    def is_enter(c):
        return c == ord('\n') or c == curses.KEY_ENTER
