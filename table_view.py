import curses
import os


class TableView(object):

    DIRECTIONS = {
        curses.KEY_UP: (-1, 0),
        curses.KEY_RIGHT: (0, 1),
        curses.KEY_DOWN: (1, 0),
        curses.KEY_LEFT: (0, -1),
    }

    # string[][] table
    # int[] column_widths
    # (int, int)[] selection
    # (int, int) position

    def __init__(self, lines, d, mode):
        self.table = [line.rstrip(os.linesep).split(d) for line in lines]
        self._column_widths = self._get_column_widths(self.table)
        self._column_offsets = self._get_column_offsets(self._column_widths)
        self.selection = set()
        self.position = (0, 0)
        self.mode = mode
        if mode:
            self.row_dict = {}
            self.column_dict = {}
            self.selected_rows = []
            self.selected_columns = []

    def draw(self, table_pad):
        """ Draws the table into screen/pad table_pad with top left corner being margin.

        :param table_pad: Pad to draw table into
        """

        # If we know the region of the table being shown, we could just update this part
        # Nothing outside of the main table is being changed ever.
        for i, row in enumerate(self.table):
            for j, content in enumerate(row):
                cell = (i, j)

                width = self._column_widths[j]
                content = content.ljust(width)

                flags = 0
                if cell == self.position:
                    flags |= curses.color_pair(2)
                elif cell in self.selection:
                    flags |= curses.A_REVERSE
                else:
                    flags |= curses.color_pair(1)

                j = self._column_offsets[j]
                # +1 to leave the top table within one row of the top
                table_pad.addstr(i, j, content, flags)

    # def draw_table_region(self, table_pad, (initial_row, initial_column), mode):

    def draw_region(self, table_pad, (initial_row, initial_column), is_select):
        """ Draws the table into screen/pad table_pad with top left corner being margin.

        :param table_pad: Pad to draw table into
        """
        current_row, current_column = self.position

        for i, row in enumerate(self.table):
            if i < min(initial_row, current_row):
                continue
            if i > max(current_row, initial_row):
                break
            for j, content in enumerate(row):
                if j < min(initial_column, current_column):
                    continue
                if j > max(current_column, initial_column):
                    break

                width = self._column_widths[j]
                content = content.ljust(width)

                flags = 0

                if i == current_row and j == current_column:
                    continue
                elif is_select:
                    flags |= curses.A_REVERSE
                else:
                    flags |= curses.color_pair(1)

                j = self._column_offsets[j]
                # +1 to leave the top table within one row of the top
                table_pad.addstr(i, j, content, flags)

    def move(self, di, dj):
        i, j = self.position
        i = self._limit(i + di, 0, len(self.table) - 1)
        j = self._limit(j + dj, 0, len(self.table[i]) - 1)
        self.position = (i, j)

    def toggle_select(self):
        if self.position in self.selection:
            self.selection.remove(self.position)
        else:
            self.selection.add(self.position)

    def clear_selection(self):
        self.selection.clear()

    # Missing the correspondent select_row
    def select_column(self):
        _, j = self.position
        for i, row in enumerate(self.table):
            if j >= len(row):
                continue
            c = (i, j)
            if c in self.selection:
                self.selection.remove(c)
            self.selection.add(c)

    def select_subtable(self, (initial_row, initial_column)):
        current_row, current_column = self.position
        for i in range(min(current_row, initial_row), max(current_row, initial_row) + 1):
            for j in range(min(current_column, initial_column), max(current_column, initial_column) + 1):
                if len(self.table[i]) > j:
                    self.selection.add((i, j))
                    self.add_output_subtable((i, j))

    def deselect_subtable(self, (initial_row, initial_column)):
        current_row, current_column = self.position
        for i in range(min(current_row, initial_row), max(current_row, initial_row) + 1):
            for j in range(min(current_column, initial_column), max(current_column, initial_column) + 1):
                if len(self.table[i]) > j:
                    if (i, j) in self.selection:
                        self.selection.remove((i, j))
                        self.remove_output_subtable((i, j))

    def add_output_subtable(self, (i, j)):
        if i in self.row_dict:
            self.row_dict[i] = self.row_dict[i] + 1
            if self.row_dict[i] == 1:
                self.selected_rows.append(i)
                self.selected_rows.sort()
        else:
            self.row_dict[i] = 1
            self.selected_rows.append(i)
            self.selected_rows.sort()
        if j in self.column_dict:
            self.column_dict[j] = self.column_dict[j] + 1
            if self.column_dict[j] == 1:
                self.selected_columns.append(j)
                self.selected_columns.sort()
        else:
            self.column_dict[j] = 1
            self.selected_columns.append(j)
            self.selected_columns.sort()

    def remove_output_subtable(self, (i, j)):
        if i in self.row_dict and self.row_dict[i] != 0:
            self.row_dict[i] = self.row_dict[i] - 1
            if self.row_dict[i] == 0:
                self.selected_rows.remove(i)
        if j in self.column_dict and self.column_dict[j] != 0:
            self.column_dict[j] = self.column_dict[j] - 1
            if self.column_dict[j] == 0:
                self.selected_columns.remove(j)

    def draw_subtable(self, output_pad):
        for i, row_number in enumerate(self.selected_rows):
            output_column_offset = 0
            for j, column_number in enumerate(self.selected_columns):
                cell = (row_number, column_number)

                if len(self.table[row_number]) <= j:
                    continue
                width = self._column_widths[column_number]
                if cell in self.selection:
                    content = self.get(cell).ljust(width)
                else:
                    content = ' '.ljust(width)
                flags = curses.color_pair(1)

                # +1 to leave the top table within one row of the top
                output_pad.addstr(i, output_column_offset, content, flags)
                output_column_offset += width

    def get(self, cell):
        i, j = cell
        return self.table[i][j]

    def column_offset(self, j):
        return self._column_offsets[j]

    @property
    def selection_content(self):
        if not self.mode:
            return [self.get(c) for c in self.selection]
        else:
            output_table = []
            for i, row_number in enumerate(self.selected_rows):
                output_table.append([])
                for j, column_number in enumerate(self.selected_columns):
                    cell = (row_number, column_number)
                    if len(self.table[row_number]) <= j:
                        continue
                    width = self._column_widths[column_number]
                    if cell in self.selection:
                        content = self.get(cell).ljust(width)
                    else:
                        content = ' '.ljust(width)
                    output_table[i].append(content)
            return output_table

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

    @staticmethod
    def _limit(x, a, b):
        return max(a, min(b, x))

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
