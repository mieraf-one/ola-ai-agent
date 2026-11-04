"""
Task Assistant Module

Provides a simple, testable utility class to manage and track tasks.
"""

from typing import List, Dict, Any


class TaskAssistant:
    """A class to manage a collection of tasks with various statuses."""

    def __init__(self) -> None:
        self.tasks: List[Dict[str, Any]] = []
        self._next_id = 1

    def add_task(self, title: str, description: str = "") -> int:
        """Add a new task and return its assigned ID."""
        if not title.strip():
            raise ValueError("Task title cannot be empty.")
        
        task = {
            "id": self._next_id,
            "title": title.strip(),
            "description": description.strip(),
            "completed": False
        }
        self.tasks.append(task)
        self._next_id += 1
        return task["id"]

    def get_task(self, task_id: int) -> Dict[str, Any]:
        """Retrieve a task by its ID."""
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        raise KeyError(f"Task with ID {task_id} not found.")

    def complete_task(self, task_id: int) -> None:
        """Mark a task as completed."""
        task = self.get_task(task_id)
        task["completed"] = True

    def list_tasks(self, completed: bool = None) -> List[Dict[str, Any]]:
        """List tasks, optionally filtered by completion status."""
        if completed is None:
            return self.tasks
        return [task for task in self.tasks if task["completed"] == completed]


if __name__ == "__main__":
    # Automatic demonstration
    assistant = TaskAssistant()
    t1 = assistant.add_task("Setup Environment", "Install Python and dependencies")
    t2 = assistant.add_task("Write Code", "Implement core features")
    
    assistant.complete_task(t1)
    
    print("All Tasks:", assistant.list_tasks())
    print("Completed Tasks:", assistant.list_tasks(completed=True))
