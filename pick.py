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
                                    standard input. The delimiter for the
                                     columns may be chosen, whereas
                                    lines are always delimited by \\n.""")

# Provided by the .sh entry file, thus not public
parser.add_argument('input', help=argparse.SUPPRESS)
parser.add_argument('output', help=argparse.SUPPRESS)

parser.add_argument('-d', '--delimiter', default=None, help="Delimiter to split the columns of the table, defaults to any whitespace char.")


def draw(stdscr, table_pad, output_pad, offset, table):
    top_offset, left_offset = offset

    mi, mj = stdscr.getmaxyx()
    # Clear all pads and windows
    stdscr.clear()
    table_pad.clear()
    output_pad.clear()

    # Draw table
    top_offset, left_offset = table.draw(stdscr,
                                         table_pad, top_offset, left_offset)

    stdscr.move(mi / 2 + 1, 0)

    # Draw instructions
    printstr(stdscr, "[q] abort / [arrows] move / [space] (un)select cell / [d] clear selection / [c] select column", curses.color_pair(3))
    printstr(stdscr, "[enter] print and copyselected cells(protip: use `pbpaste | ...` to pipe forward)", curses.color_pair(3))
    printstr(stdscr)

    # Output preview
    if table.selection:
        printstr(stdscr, "[{}] cells selected".format(len(table.selection)), curses.color_pair(3))
        output_pad.move(0, 0)
        for content in table.selection_content:
            i, j = output_pad.getyx()
            writestr(output_pad, " |=> ", curses.color_pair(1))
            printstr(output_pad, content, curses.color_pair(1))
            output_pad.move(i + 1, j)

    # Refresh
    stdscr.refresh()
    table_pad.refresh(top_offset, table.get_column_offset(left_offset), 0, 0, mi / 2 - 1, mj - 1)
    output_pad.refresh(0, 0, mi / 2 + 6, 0, mi - 1, mj - 1)
    return (top_offset, left_offset)


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

    offset = (0, 0)
    table = TableView(lines, d)
    table_pad = curses.newpad(table.height + 1, table.width)
    # TODO: Get width of output pad from column offsets
    output_pad = curses.newpad(table.height * table.column_number + 1, table.width)
    draw(stdscr, table_pad, output_pad, offset, table)

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
        offset = draw(stdscr, table_pad, output_pad, offset, table)


if __name__ == '__main__':
    exit(main())

raise AssertionError('Only use this script from a terminal')
