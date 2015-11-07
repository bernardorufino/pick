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