# pick
**pick** is a command line tool that lets you select parts of the input before printing to the standard output. It's quite useful to use in the middle of a piped sequence of commands.

**pick** parses the input trying to understand its table structure and presents an interactive UI to select which parts of the input you want. It has 2 output modes: **list** and **table**. 

- **List mode**: outputs a list divided by '\n', handy for selecting sublists before executing commands on some input. 
- **Table mode**: lets you select parts of the table and constructs the final subtable, useful for filtering huge tables that some commands output.
