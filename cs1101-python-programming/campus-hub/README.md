# Campus Life & Productivity Hub

A command-line task and exam manager written in Python for CS 1101. It saves
data between sessions and applies every concept from Units 1 to 8.

## Features

- Add, complete, reschedule, delete and search tasks by tag
- Exam tracking with an automatic daily study plan
- Overdue detection and a progress bar
- Saves and loads tasks from a file; writes summary reports

## How to run

    git clone git@github.com:OcollotheEnigma/cs-degree-portfolio.git
    cd cs-degree-portfolio/cs1101-python-programming/campus-hub
    python3 main.py

## Where each unit appears

| Unit | Where it appears |
|------|------------------|
| 1 Basics | typed values (str, int, float, bool), `input()`/`print()`, f-strings |
| 2 Conditionals | `Task.__init__` validation, `Task.label()`, menu routing |
| 3 Loops | `while True` menu, `ask_date()` retry loop, `for` + `continue` in `load()`, `break` on exit |
| 4 Functions | helpers (`ask`, `progress_bar`), global constants vs local variables, menu of functions |
| 5 Lists/Tuples | list comprehensions in `TaskManager`, `PRIORITIES` tuple, `stats()` returns a tuple |
| 6 Dicts/Sets | `tasks` dict (ID -> Task), `MENU` dict, tag `set` + union in `all_tags()` |
| 7 Strings/Files | `.strip() .lower() .split() .join()`, read/write/append modes, `try/except/finally` |
| 8 Libraries/OOP | `os`, `random`, `datetime`, `math`; classes, encapsulation, classmethods, inheritance, polymorphism |

Task input format: `Name, YYYY-MM-DD[, Priority[, tag1 tag2]]`
Data is saved to `Hub_Logs/tasks.txt` and reloaded on next launch.

## Extension challenges
1. Add recurring tasks (weekly) as a new subclass.
2. Export tasks to CSV with the `csv` module.
3. Add unit tests with `unittest`.
