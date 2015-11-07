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


def pbcopy(data):
    default_command = ['echo']

    if sys.platform == 'linux2':
        command = ['xsel', '--clipboard']
    elif sys.platform == 'darwin':
        command = ['pbcopy']
    else:
        command = ['clip']

    # Try to run the specified command and if it is not available, just pipe
    # the result using the |default_command|.
    try:
        p = subprocess.Popen(command, stdin=subprocess.PIPE)
        p.communicate(data)
    except OSError:
        msg = ("Warning: Couldn't copy to the clipboard. Only Linux and Mac "
            "are supported. If you are using one of these systems, check the "
            "requirements section at https://github.com/bernardorufino/pick. "
            "")
        print msg
        p = subprocess.Popen(default_command, stdin=subprocess.PIPE)
        p.communicate(data)


def limit(x, a, b):
    return max(a, min(b, x))