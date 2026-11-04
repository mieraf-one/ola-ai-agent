"""
Unit Tests for TaskAssistant
"""

import pytest
from task_assistant import TaskAssistant


def test_add_task():
    assistant = TaskAssistant()
    task_id = assistant.add_task("Test Title", "Test Description")
    
    assert task_id == 1
    task = assistant.get_task(task_id)
    assert task["title"] == "Test Title"
    assert task["description"] == "Test Description"
    assert task["completed"] is False


def test_add_task_empty_title():
    assistant = TaskAssistant()
    with pytest.raises(ValueError):
        assistant.add_task("   ", "Empty title test")


def test_complete_task():
    assistant = TaskAssistant()
    t_id = assistant.add_task("Complete Me")
    
    assert assistant.get_task(t_id)["completed"] is False
    assistant.complete_task(t_id)
    assert assistant.get_task(t_id)["completed"] is True


def test_list_tasks():
    assistant = TaskAssistant()
    assistant.add_task("Task 1")
    t2 = assistant.add_task("Task 2")
    assistant.complete_task(t2)
    
    all_tasks = assistant.list_tasks()
    assert len(all_tasks) == 2
    
    completed_tasks = assistant.list_tasks(completed=True)
    assert len(completed_tasks) == 1
    assert completed_tasks[0]["title"] == "Task 2"
    
    pending_tasks = assistant.list_tasks(completed=False)
    assert len(pending_tasks) == 1
    assert pending_tasks[0]["title"] == "Task 1"


def test_get_nonexistent_task():
    assistant = TaskAssistant()
    with pytest.raises(KeyError):
        assistant.get_task(999)
