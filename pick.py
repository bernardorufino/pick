#!/usr/bin/env python

import curses
import inspect
import argparse
import os
from utils import printstr, writestr, pbcopy
from table_view import TableView

ss = inspect.cleandoc

parser = argparse.ArgumentParser(prog='pick',
                                 description="""Interactively lets the user pick a cell in a table given to the
                                                standard input. The delimiter for the columns may be chosen, whereas
                                                lines are always delimited by \\n.""")

# Provided by the .sh entry file, thus not public
parser.add_argument('input', help=argparse.SUPPRESS)
parser.add_argument('output', help=argparse.SUPPRESS)

parser.add_argument('-d', '--delimiter', default=None,
                    help="Delimiter to split the columns of the table, defaults to any whitespace char.")

parser.add_argument('-s', '--subtable', default=False, action='store_true',
                    help="Enter in a mode that outputs a formatted subtable of the input.")


def draw(stdscr, table_pad, output_pad, margin, (top_offset, left_offset), table, resizing, redraw_output, mode, state, initial_position=(0,0)):
    top_margin, left_margin = margin

    mi, mj = stdscr.getmaxyx()
    table_pad_height = mi / 2 - top_margin
    table_pad_width = mj - left_margin

    # Clear all pads and windows


    #if resizing:
    stdscr.clear()
    if state == 0:
        table_pad.clear()
    if redraw_output:
        output_pad.clear()

    # Draw table
    table.draw(table_pad)
    if state == 1:
        table.draw_region(table_pad, initial_position, True)
    elif state == 2:
        table.draw_region(table_pad, initial_position, False)

    # Scroll up/down
    i, j = table.position
    if i > top_offset + table_pad_height - 1:
        top_offset += 1
    elif i < top_offset:
        top_offset -= 1
    # There's no guarantee that shifting the table one column to the right will make the entire column of the current
    # position visible bc unlike rows columns can have variable width. So, we shift until the column is fully visible.
    shift_left = lambda left_offset: table.column_offset(j + 1) > table.column_offset(left_offset) + table_pad_width - 1
    if shift_left(left_offset):
        while shift_left(left_offset):
            left_offset += 1
    elif resizing:
        while left_offset >= 1 and table.column_offset(j + 1) - table.column_offset(left_offset - 1) < table_pad_width:
            left_offset -= 1

    if j < left_offset:
        left_offset -= 1

    # Draw instructions
    stdscr.move(top_margin + table_pad_height + 1, left_margin)
    if mode:
        if state == 0:
            printstr(stdscr, "Move Mode", curses.color_pair(3))
        elif state == 1:
            printstr(stdscr, "Select Mode", curses.color_pair(5))
        else:
            printstr(stdscr, "Deselect Mode", curses.color_pair(6))
    printstr(stdscr, "[q] abort / [arrows] move / [space] (un)select cell / [d] clear selection / [c] select column", curses.color_pair(3))
    printstr(stdscr, "[enter] print and copy selected cells (protip: use `pbpaste | ...` to pipe forward)", curses.color_pair(3))
    printstr(stdscr)

    # Output preview
    if redraw_output and table.selection and not mode:
        output_pad.move(0, 0)
        printstr(output_pad, "[{}] cells selected".format(len(table.selection)), curses.color_pair(3))
        for content in table.selection_content:
            i, j = output_pad.getyx()
            writestr(output_pad, " |=> ", curses.color_pair(1))
            printstr(output_pad, content, curses.color_pair(1))
            output_pad.move(i + 1, j)
    elif redraw_output and table.selection and mode:
        table.draw_subtable(output_pad)

    # Refresh
    stdscr.noutrefresh()
    table_pad.noutrefresh(top_offset, table.column_offset(left_offset), top_margin, left_margin,
                          top_margin + table_pad_height - 1, left_margin + table_pad_width - 1)
    output_pad.noutrefresh(0, 0, top_margin + table_pad_height + 4, left_margin, mi - 1, mj - 1)
    curses.doupdate()

    return top_offset, left_offset


def main():
    args = parser.parse_args()
    with open(args.input, 'r') as f:
        lines = f.readlines()
    d = args.delimiter
    mode = args.subtable
    output = curses.wrapper(main_curses, lines, d, mode)
    if output:
        pbcopy(output)
        with open(args.output, 'w') as f:
            f.write(output + os.linesep)


def process_output(table, mode):
    if table.selection and not mode:
        cells = table.selection_content
        return os.linesep.join(cells)
    elif table.selection and mode:
        table_cells = table.selection_content
        cells = []
        for row in table_cells:
            cells.append(' '.join(row))
        return os.linesep.join(cells)
    else:
        return None


# TODO: Non-uniform table (with merges and different size of columns/rows)
# TODO: Change tables and scroll in both of them
def main_curses(stdscr, lines, d, mode):
    curses.curs_set(0)
    curses.init_pair(1, 251, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, 237, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)

    margin = (1, 2)
    table_offset = (0, 0)
    table = TableView(lines, d, mode)
    table_pad = curses.newpad(table.height + 1, table.width)
    # TODO: Get width of output pad from column offsets
    if mode:
        output_pad = curses.newpad(table.height + 1, table.width)
    else:
        output_pad = curses.newpad(table.ncells + 1, table.width)
    draw(stdscr, table_pad, output_pad, margin, table_offset, table, False, True, mode, 0)

    if mode:
        MOVE_STATE = 0
        SELECT_STATE = 1
        DESELECT_STATE = 2
        initial_position = (0, 0)
        state = MOVE_STATE
        while True:
            c = stdscr.getch()
            redraw_output = False
            if state == MOVE_STATE:
                if c == ord('q'):
                    return
                elif c == ord(' '):
                    state = SELECT_STATE
                    initial_position = table.position
                    redraw_output = True
                elif c == ord('d'):
                    state = DESELECT_STATE
                    initial_position = table.position
                    redraw_output = True
                elif c in TableView.DIRECTIONS.keys():
                    di, dj = TableView.DIRECTIONS[c]
                    table.move(di, dj)
                elif c == ord('\n') or c == curses.KEY_ENTER:
                    return process_output(table, mode)
            elif state == SELECT_STATE:
                if c in TableView.DIRECTIONS.keys():
                    di, dj = TableView.DIRECTIONS[c]
                    table.move(di, dj)
                elif c == ord(' '):
                    state = MOVE_STATE
                    table.select_subtable(initial_position)
                    redraw_output = True

            elif state == DESELECT_STATE:
                if c in TableView.DIRECTIONS.keys():
                    di, dj = TableView.DIRECTIONS[c]
                    table.move(di, dj)
                elif c == ord(' '):
                    state = MOVE_STATE
                    table.deselect_subtable(initial_position)
                    redraw_output = True
            # else:
            resizing = (c == -1)
            table_offset = draw(stdscr, table_pad, output_pad, margin, table_offset, table,
                                resizing, redraw_output, mode, state, initial_position)

    else:
        while True:
            c = stdscr.getch()
            redraw_output = False
            if c == ord('q'):
                return
            elif c in TableView.DIRECTIONS.keys():
                di, dj = TableView.DIRECTIONS[c]
                table.move(di, dj)
            elif c == ord(' '):
                table.toggle_select()
                redraw_output = True
            elif c == ord('d'):
                table.clear_selection()
                redraw_output = True
            elif c == ord('c'):
                table.select_column()
                redraw_output = True
            elif c == ord('\n') or c == curses.KEY_ENTER:
                return process_output(table, mode)
            resizing = (c == -1)
            table_offset = draw(stdscr, table_pad, output_pad, margin, table_offset, table,
                                resizing, redraw_output, mode, 0)


if __name__ == '__main__':
    exit(main())

raise AssertionError('Only use this script from a terminal')
