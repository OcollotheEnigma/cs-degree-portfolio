"""
main.py - Interface, control flow and automation for the Campus Hub.
Run with:  python main.py
"""
import os
import random
from datetime import datetime, date

from models import Task, ExamTask, TaskManager, PRIORITIES, parse_date

LOG_DIR = "Hub_Logs"
DATA_FILE = os.path.join(LOG_DIR, "tasks.txt")
LOG_FILE = os.path.join(LOG_DIR, "daily_activity.txt")
SUMMARY_FILE = os.path.join(LOG_DIR, "summary.txt")

QUOTES = [
    "Consistency is the secret code to mastering Python logic.",
    "Small daily progress adds up to massive capabilities.",
    "Errors are just debugging steps toward mastery.",
    "Done is better than perfect - ship the task.",
]


# ---------------------------------------------------------------- helpers ---
def ask(prompt):
    return input(prompt).strip()


def ask_date(prompt):
    """Keep asking until a valid date is entered (Unit 3 loop + Unit 7 try)."""
    while True:
        try:
            return parse_date(ask(prompt))
        except ValueError:
            print("  Invalid date. Use YYYY-MM-DD (e.g. 2026-11-30).")


def ask_choice(prompt, options):
    while True:
        value = ask(prompt).capitalize()
        if value in options:
            return value
        print(f"  Choose one of: {', '.join(options)}")


def log_activity(message):
    """Append a timestamped line to the log file (append mode 'a')."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{stamp}] {message}\n")
    except OSError as e:
        print(f"  (log failed: {e})")


def print_table(pairs):
    if not pairs:
        print("  Nothing to show.")
        return
    print(f"\n{'ID':<5}{'Task':<24} | {'Due':<10} | {'Prio':<6} | Status")
    print("-" * 72)
    for task_id, task in pairs:
        print(f"{task_id:<5}", end="")
        task.show()


def progress_bar(percent, width=20):
    filled = int(width * percent / 100)
    return "[" + "#" * filled + "-" * (width - filled) + f"] {percent}%"


# ---------------------------------------------------------------- actions ---
def add_task(hub):
    print("\nFormat: Name, YYYY-MM-DD[, Priority[, tag1 tag2]]")
    try:
        task = Task.from_string(ask("> "))
        print(f"  Added as {hub.add(task)}.")
        log_activity(f"Added task '{task.name}'")
    except ValueError as e:
        print(f"  Error: {e}")


def add_exam(hub):
    name = ask("Exam name: ")
    subject = ask("Subject: ")
    due = ask_date("Exam date (YYYY-MM-DD): ")
    try:
        hours = float(ask("Total study hours planned: "))
        exam = ExamTask(name, due, subject, hours, tags={"exam", subject.lower()})
    except ValueError as e:
        print(f"  Error: {e}")
        return
    print(f"  Added as {hub.add(exam)}.")
    log_activity(f"Added exam '{name}'")


def view_tasks(hub):
    print_table(hub.sorted_by_due())
    total, done, pending, overdue, pct = hub.stats()
    print(f"\n  Progress {progress_bar(pct)}  ({done}/{total} done, {overdue} overdue)")


def complete_task(hub):
    task = hub.get(ask("Task ID to complete: "))
    if task is None:
        print("  Task ID not found.")
    elif task.get_status() == "Completed":
        print("  Already completed.")
    else:
        task.mark_complete()
        print(f"  Great work! '{task.name}' completed.")
        log_activity(f"Completed '{task.name}'")


def reschedule_task(hub):
    task = hub.get(ask("Task ID to reschedule: "))
    if task is None:
        print("  Task ID not found.")
        return
    task.reschedule(ask_date("New date (YYYY-MM-DD): "))
    print(f"  Rescheduled to {task.due_date}.")


def delete_task(hub):
    removed = hub.delete(ask("Task ID to delete: "))
    print(f"  Deleted '{removed.name}'." if removed else "  Task ID not found.")


def search_by_tag(hub):
    tags = sorted(hub.all_tags())
    print("  Available tags:", ", ".join(tags) if tags else "(none yet)")
    if tags:
        print_table(hub.by_tag(ask("Tag to search: ")))


def motivation(hub):
    quote = random.choice(QUOTES)
    print(f"\n  Daily Motivation: {quote}")
    log_activity(f"Quote: {quote}")


def write_summary(hub):
    """Write a report; try/except/finally shows safe file handling (Unit 7)."""
    total, done, pending, overdue, pct = hub.stats()
    report = None
    try:
        report = open(SUMMARY_FILE, "w", encoding="utf-8")
        report.write(f"CAMPUS HUB SUMMARY - {date.today()}\n{'=' * 40}\n")
        report.write(f"Total: {total} | Done: {done} | Pending: {pending} | "
                     f"Overdue: {overdue}\n{progress_bar(pct)}\n\nPENDING:\n")
        for task_id, task in hub.pending():
            report.write(f"  {task_id}: {task} [{task.priority}] - {task.label()}\n")
        print(f"  Summary written to {SUMMARY_FILE}")
    except OSError as e:
        print(f"  Could not write summary: {e}")
    finally:
        if report:
            report.close()


# ------------------------------------------------------------------- menu ---
# Unit 6 + 4: a dictionary mapping menu choices to (label, function) pairs.
MENU = {
    "1": ("Add task", add_task),
    "2": ("Add exam (with study plan)", add_exam),
    "3": ("View all tasks", view_tasks),
    "4": ("Mark task complete", complete_task),
    "5": ("Reschedule task", reschedule_task),
    "6": ("Delete task", delete_task),
    "7": ("Search by tag", search_by_tag),
    "8": ("Daily motivation", motivation),
    "9": ("Write summary report", write_summary),
    "0": ("Save & exit", None),
}


def display_menu():
    print("\n" + "=" * 42)
    print("  CAMPUS LIFE & PRODUCTIVITY HUB  v2.0")
    print("=" * 42)
    for key, (label, _) in MENU.items():
        print(f"  {key}. {label}")


def run_hub():
    if not os.path.exists(LOG_DIR):          # Unit 8: os module
        os.mkdir(LOG_DIR)

    hub = TaskManager()
    count = hub.load(DATA_FILE)
    print(f"Welcome! Loaded {count} saved task(s).")
    overdue = hub.overdue()
    if overdue:
        print(f"  Heads up: {len(overdue)} task(s) are overdue!")

    while True:                               # Unit 3: persistent loop
        display_menu()
        choice = ask("Select an option: ")
        if choice == "0":
            if hub.save(DATA_FILE):
                print("Saved. Have a productive day!")
            break
        elif choice in MENU:
            MENU[choice][1](hub)              # call the chosen function
        else:
            print("Invalid selection.")


if __name__ == "__main__":
    run_hub()
