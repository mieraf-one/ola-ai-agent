import json
import os

DEFAULT_FILENAME = "todos.json"


def load_tasks(filename=DEFAULT_FILENAME):
    """Load tasks from a JSON file. Returns an empty list if file doesn't exist or is invalid."""
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except (json.JSONDecodeError, IOError):
        pass
    return []


def save_tasks(tasks, filename=DEFAULT_FILENAME):
    """Save tasks to a JSON file."""
    with open(filename, "w") as f:
        json.dump(tasks, f, indent=4)


def add_task(tasks, title):
    """Add a new task to the list and return the updated list."""
    if not title or not title.strip():
        raise ValueError("Task title cannot be empty.")
    new_task = {
        "id": len(tasks) + 1 if not tasks else max(t["id"] for t in tasks) + 1,
        "title": title.strip(),
        "completed": False
    }
    tasks.append(new_task)
    return tasks


def view_tasks(tasks):
    """Return the list of tasks."""
    return tasks


def delete_task(tasks, task_id):
    """Delete a task by its ID. Raises ValueError if task not found."""
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            return tasks.pop(i)
    raise ValueError(f"Task with ID {task_id} not found.")


def complete_task(tasks, task_id):
    """Mark a task as completed."""
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            return task
    raise ValueError(f"Task with ID {task_id} not found.")


if __name__ == "__main__":
    print("--- Automated Demonstration ---")
    
    # Use a temporary file for demo
    demo_file = "demo_todos.json"
    if os.path.exists(demo_file):
        os.remove(demo_file)

    tasks = load_tasks(demo_file)
    print("1. Initial tasks loaded:", view_tasks(tasks))

    print("2. Adding tasks...")
    add_task(tasks, "Learn Python")
    add_task(tasks, "Build a Todo App")
    save_tasks(tasks, demo_file)
    for t in view_tasks(tasks):
        print(f"   [{ 'x' if t['completed'] else ' ' }] {t['id']}: {t['title']}")

    print("3. Completing task ID 1...")
    complete_task(tasks, 1)
    save_tasks(tasks, demo_file)
    for t in view_tasks(tasks):
        print(f"   [{ 'x' if t['completed'] else ' ' }] {t['id']}: {t['title']}")

    print("4. Deleting task ID 2...")
    delete_task(tasks, 2)
    save_tasks(tasks, demo_file)
    print("   Remaining tasks:", view_tasks(tasks))

    # Cleanup demo file
    if os.path.exists(demo_file):
        os.remove(demo_file)
    print("--- Demonstration Complete ---")
