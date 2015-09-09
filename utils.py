import subprocess


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
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.communicate(data)
