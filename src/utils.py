import subprocess
import sys


def printstr(stdscr, *args):
    i, j = stdscr.getyx()
    mi, _ = stdscr.getmaxyx()
    if not args:
        args = [""]
    stdscr.addstr(*args)
    if i + 1 < mi:
        stdscr.move(i + 1, j)


def writestr(stdscr, *args):
    stdscr.addstr(*args)


def try_copy_to_clipboard(data):
    if sys.platform == 'linux2':
        command = ['xsel', '--clipboard']
    elif sys.platform == 'darwin':
        command = ['pbcopy']
    else:
        return False

    try:
        p = subprocess.Popen(command, stdin=subprocess.PIPE)
        p.communicate(data)
        return p.returncode == 0
    except:
        return False


def limit(x, a, b):
    return max(a, min(b, x))


def join_line(cells, delimiter):
    if delimiter is None:
        assert len(cells) == 1
        return cells[0]
    return delimiter.join(cells)


def split_line(line, delimiter):
    if delimiter is None:
        return [line]
    d = None if delimiter == ' ' else delimiter
    return line.split(d)
