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


def draw(stdscr, table_pad, output_pad, margin, (top_offset, left_offset), table, resizing):
    top_margin, left_margin = margin

    mi, mj = stdscr.getmaxyx()
    table_pad_height = mi / 2 - top_margin
    table_pad_width = mj - left_margin

    # Clear all pads and windows
    stdscr.clear()
    table_pad.clear()
    output_pad.clear()

    # Draw table
    table.draw(table_pad)

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
    printstr(stdscr, "[q] abort / [arrows] move / [space] (un)select cell / [d] clear selection / [c] select column", curses.color_pair(3))
    printstr(stdscr, "[enter] print and copy selected cells (protip: use `pbpaste | ...` to pipe forward)", curses.color_pair(3))
    printstr(stdscr)

    # Output preview
    if table.selection:
        output_pad.move(0, 0)
        printstr(output_pad, "[{}] cells selected".format(len(table.selection)), curses.color_pair(3))
        for content in table.selection_content:
            i, j = output_pad.getyx()
            writestr(output_pad, " |=> ", curses.color_pair(1))
            printstr(output_pad, content, curses.color_pair(1))
            output_pad.move(i + 1, j)

    # Refresh
    stdscr.refresh()
    table_pad.refresh(top_offset, table.column_offset(left_offset), top_margin, left_margin,
                      top_margin + table_pad_height - 1, left_margin + table_pad_width - 1)
    output_pad.refresh(0, 0, top_margin + table_pad_height + 4, left_margin, mi - 1, mj - 1)
    return top_offset, left_offset


def main():
    args = parser.parse_args()
    with open(args.input, 'r') as f:
        lines = f.readlines()
    d = args.delimiter
    output = curses.wrapper(main_curses, lines, d)
    if output:
        pbcopy(output)
        with open(args.output, 'w') as f:
            f.write(output + os.linesep)


def process_output(table):
    if table.selection:
        cells = table.selection_content
        return os.linesep.join(cells)
    else:
        return None


# TODO: Non-uniform table (with merges and different size of columns/rows)
# TODO: Change tables and scroll in both of them
def main_curses(stdscr, lines, d):
    curses.curs_set(0)
    curses.init_pair(1, 251, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, 237, curses.COLOR_BLACK)

    margin = (1, 2)
    table_offset = (0, 0)
    table = TableView(lines, d)
    table_pad = curses.newpad(table.height + 1, table.width)
    # TODO: Get width of output pad from column offsets
    output_pad = curses.newpad(table.ncells + 1, table.width)
    draw(stdscr, table_pad, output_pad, margin, table_offset, table, False)

    while True:
        c = stdscr.getch()
        if c == ord('q'):
            return
        elif c in TableView.DIRECTIONS.keys():
            di, dj = TableView.DIRECTIONS[c]
            table.move(di, dj)
        elif c == ord(' '):
            table.toggle_select()
        elif c == ord('d'):
            table.clear_selection()
        elif c == ord('c'):
            table.select_column()
        elif c == ord('\n') or c == curses.KEY_ENTER:
            print('<enter> => print and copy selected cells')
            return process_output(table)
        resizing = (c == -1)
        table_offset = draw(stdscr, table_pad, output_pad, margin, table_offset, table, resizing)


if __name__ == '__main__':
    exit(main())

raise AssertionError('Only use this script from a terminal')
