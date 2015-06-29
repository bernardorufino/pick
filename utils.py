import subprocess


def printstr(stdscr, *args):
    i, j = stdscr.getyx()
    if not args:
        args = [""]
    stdscr.addstr(*args)
    stdscr.move(i + 1, j)


def writestr(stdscr, *args):
    stdscr.addstr(*args)


def pbcopy(data):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.communicate(data)
