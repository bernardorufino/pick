#!/usr/bin/env python

import curses
import inspect
import argparse
import os
from enum import Enum

from table.selectable_table import SelectableTable
from utils import pbcopy
from view import View

ss = inspect.cleandoc

parser = argparse.ArgumentParser(prog='pick',
                                 description="""Interactively lets the user pick a cell in a table given to the
                                                standard input. The delimiter for the columns may be chosen, whereas
                                                lines are always delimited by \\n.""")

# Provided by the .sh entry file, thus not public
parser.add_argument('input', help=argparse.SUPPRESS)
parser.add_argument('output', help=argparse.SUPPRESS)

parser.add_argument('-d', '--delimiter', default=' ',
                    help="Delimiter to split the columns of the table, defaults to any whitespace char.")

parser.add_argument('-t', '--table', default=False, action='store_true',
                    help="Enter in subtable selection mode. In this mode instead of selecting separate cells and "
                         "returning a list as output, you select a structured portion of the table and the output is "
                         "also a table obtained by concatenating the subtables selected.")


class SelectionMode(Enum):
    list = 0
    table = 1


def process_input(input_table, delimiter):
    if delimiter == ' ':
        delimiter = None
    return [line.rstrip(os.linesep).split(delimiter) for line in input_table]


def main():
    args = parser.parse_args()
    mode = SelectionMode.table if args.table else SelectionMode.list

    if mode == SelectionMode.table:
        from selectors.multi_selector import MultiSelector
        selector = MultiSelector()
        from output_processors.table_processor import TableProcessor
        output_processor = TableProcessor()
    else:
        from selectors.single_selector import SingleSelector
        selector = SingleSelector()
        from output_processors.list_processor import ListProcessor
        output_processor = ListProcessor()

    with open(args.input, 'r') as f:
        rows = f.readlines()
    input_table = process_input(rows, args.delimiter)
    table = SelectableTable(input_table)

    view = View(table, selector, output_processor, args)
    output = curses.wrapper(view.run)

    if output:
        pbcopy(output)
        with open(args.output, 'w') as f:
            f.write(output + os.linesep)


if __name__ == '__main__':
    exit(main())


raise AssertionError('Only use this script from a terminal')