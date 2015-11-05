# pick
**pick** is a command line tool that lets you select parts of the input before printing to the standard output. It's useful to use in the middle of a piped sequence of commands.

**pick** parses the input trying to understand its table structure and presents an interactive UI to select which parts of the input you want. It has 2 output modes: **list** and **table**. 

- **List mode**: outputs a list divided by '\n', handy for selecting sublists before executing commands on some input. 
- **Table mode**: lets you select parts of the table and constructs the final subtable, useful for filtering huge tables that some commands output.

## Installing

### Homebrew
* `brew tap bernardorufino/pick`
* `brew install pick`

### Manual
* `cd <install-dir>`
* `git clone -b release --depth 1 https://github.com/bernardorufino/pick.git .`
* `ln -s $(pwd)/pick.sh /usr/local/pick  # or other directory present in the $PATH variable`

## Using
Give it a try:
* `ls -l | pick  # print files and copy to clipboard`
* `ls | pick | xargs rm  # select files in current directory before removing`

