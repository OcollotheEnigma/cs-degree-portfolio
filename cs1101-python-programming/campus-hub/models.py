"""
models.py - Object-oriented layer of the Campus Life & Productivity Hub.

Units shown here:
  U1 data types | U2 conditionals | U3 loops | U4 functions & scope
  U5 lists/tuples | U6 dicts/sets | U7 strings & files | U8 modules & OOP
"""
from datetime import datetime, date   # Unit 8: standard library
import math                           # Unit 8

# ---- Module-level constants (Unit 4: global scope) -------------------------
DATE_FORMAT = "%Y-%m-%d"
PRIORITIES = ("Low", "Medium", "High")      # Unit 5: tuple = fixed, unchangeable
FIELD_SEP = "|"                              # separator used in the save file


def parse_date(text):
    """Unit 4 + 7: function that cleans a string and converts it to a date."""
    return datetime.strptime(text.strip(), DATE_FORMAT).date()


class Task:
    """A single campus task. Demonstrates encapsulation and class methods."""

    total_created = 0   # class attribute shared by all Task objects

    def __init__(self, name, due_date, priority="Medium", tags=None, status="Pending"):
        # Unit 2: validation with conditionals
        name = name.strip()
        if not name:
            raise ValueError("Task name cannot be empty.")
        if FIELD_SEP in name:
            raise ValueError(f"Task name cannot contain '{FIELD_SEP}'.")
        if priority not in PRIORITIES:
            raise ValueError(f"Priority must be one of {PRIORITIES}.")

        self.name = name
        self.due_date = due_date                 # a datetime.date object
        self.priority = priority
        self.tags = set(tags) if tags else set()  # Unit 6: set = no duplicates
        self.__status = status                    # private (name-mangled) attribute
        Task.total_created += 1

    # ---- Alternative constructors (classmethods) ---------------------------
    @classmethod
    def from_string(cls, text):
        """Parse 'Name, 2026-11-01[, Priority[, tag1 tag2]]' into a Task."""
        parts = [p.strip() for p in text.split(",")]
        if len(parts) < 2:
            raise ValueError("Use the format: Name, YYYY-MM-DD[, Priority[, tags]]")
        name, due = parts[0], parse_date(parts[1])
        priority = parts[2].capitalize() if len(parts) > 2 and parts[2] else "Medium"
        tags = parts[3].lower().split() if len(parts) > 3 else []
        return cls(name, due, priority, tags)

    @classmethod
    def from_record(cls, line):
        """Rebuild a Task (or ExamTask) from one line of the save file."""
        f = line.rstrip("\n").split(FIELD_SEP)
        kind, name, due, priority, tags, status = f[:6]
        tag_set = set(tags.split(";")) if tags else set()
        if kind == "EXAM":
            return ExamTask(name, parse_date(due), f[6], float(f[7]),
                            priority, tag_set, status)
        return cls(name, parse_date(due), priority, tag_set, status)

    # ---- Encapsulation: controlled access to the private status ------------
    def get_status(self):
        return self.__status

    def mark_complete(self):
        self.__status = "Completed"

    def reschedule(self, new_date):
        self.due_date = new_date

    # ---- Computed properties -----------------------------------------------
    def days_left(self):
        return (self.due_date - date.today()).days

    def is_overdue(self):
        return self.__status == "Pending" and self.days_left() < 0

    # ---- Output / persistence ----------------------------------------------
    def label(self):
        """Return a status label for display (Unit 2: if/elif/else)."""
        if self.__status == "Completed":
            return "Done"
        elif self.is_overdue():
            return f"OVERDUE by {abs(self.days_left())}d"
        elif self.days_left() == 0:
            return "Due TODAY"
        return f"{self.days_left()}d left"

    def show(self):
        tags = " ".join(f"#{t}" for t in sorted(self.tags))
        print(f"{self.name:<24} | {self.due_date} | {self.priority:<6} | "
              f"{self.label():<16} {tags}")

    def to_record(self):
        return FIELD_SEP.join(["TASK", self.name, self.due_date.isoformat(),
                               self.priority, ";".join(sorted(self.tags)),
                               self.__status])

    def __str__(self):
        return f"{self.name} (due {self.due_date})"

    def __repr__(self):
        return f"Task({self.name!r}, {self.due_date.isoformat()!r}, {self.priority!r})"


class ExamTask(Task):
    """Inheritance: an exam IS a task, plus a subject and a study plan."""

    def __init__(self, name, due_date, subject, study_hours,
                 priority="High", tags=None, status="Pending"):
        super().__init__(name, due_date, priority, tags, status)
        self.subject = subject
        self.study_hours = study_hours

    def study_plan(self):
        """Unit 8 math module: hours per day, rounded up."""
        days = max(self.days_left(), 1)
        return math.ceil(self.study_hours / days * 10) / 10

    def show(self):                      # polymorphism: overrides Task.show
        super().show()
        print(f"{'':<24}   Subject: {self.subject} | "
              f"Study {self.study_plan()} h/day for {self.study_hours} h total")

    def to_record(self):
        return super().to_record().replace("TASK", "EXAM", 1) + \
               f"{FIELD_SEP}{self.subject}{FIELD_SEP}{self.study_hours}"


class TaskManager:
    """Owns the dictionary of tasks and all queries/file operations."""

    def __init__(self):
        self.tasks = {}        # Unit 6: ID -> Task object
        self._next_id = 1

    def add(self, task):
        task_id = f"T{self._next_id}"
        self._next_id += 1
        self.tasks[task_id] = task
        return task_id

    def get(self, task_id):
        return self.tasks.get(task_id.upper())

    def delete(self, task_id):
        return self.tasks.pop(task_id.upper(), None)

    # ---- Queries built with list comprehensions (Unit 5) -------------------
    def pending(self):
        return [(i, t) for i, t in self.tasks.items() if t.get_status() == "Pending"]

    def overdue(self):
        return [(i, t) for i, t in self.tasks.items() if t.is_overdue()]

    def by_tag(self, tag):
        return [(i, t) for i, t in self.tasks.items() if tag.lower() in t.tags]

    def sorted_by_due(self):
        return sorted(self.tasks.items(), key=lambda pair: pair[1].due_date)

    def all_tags(self):
        """Unit 6: union of every task's tag set."""
        result = set()
        for t in self.tasks.values():
            result |= t.tags
        return result

    def stats(self):
        """Return a tuple (total, done, pending, overdue, percent_done)."""
        total = len(self.tasks)
        done = total - len(self.pending())
        percent = round(done / total * 100) if total else 0
        return total, done, len(self.pending()), len(self.overdue()), percent

    # ---- File handling (Unit 7) --------------------------------------------
    def save(self, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                for t in self.tasks.values():
                    f.write(t.to_record() + "\n")
            return True
        except OSError as e:
            print(f"Could not save: {e}")
            return False

    def load(self, path):
        """Load tasks; returns how many were loaded. Skips corrupt lines."""
        loaded = 0
        try:
            f = open(path, "r", encoding="utf-8")
        except FileNotFoundError:
            return 0                       # first run: nothing to load
        try:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue               # Unit 3: continue
                try:
                    self.add(Task.from_record(line))
                    loaded += 1
                except (ValueError, IndexError):
                    print(f"  Skipped corrupt line {line_no} in {path}")
        finally:
            f.close()                      # always runs
        return loaded
