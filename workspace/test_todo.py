import os
import pytest
from todo import (
    load_tasks,
    save_tasks,
    add_task,
    view_tasks,
    delete_task,
    complete_task
)


@pytest.fixture
def pyt_temp_file(tmp_path):
    return str(tmp_path / "test_todos.json")


def test_add_task():
    tasks = []
    add_task(tasks, "Test Task 1")
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Test Task 1"
    assert tasks[0]["id"] == 1
    assert tasks[0]["completed"] is False

    # Test adding empty task raises ValueError
    with pytest.raises(ValueError):
        add_task(tasks, "   ")


def test_view_tasks():
    tasks = [{"id": 1, "title": "Task", "completed": False}]
    assert view_tasks(tasks) == tasks


def test_delete_task():
    tasks = [
        {"id": 1, "title": "Task 1", "completed": False},
        {"id": 2, "title": "Task 2", "completed": False}
    ]
    deleted = delete_task(tasks, 1)
    assert deleted["id"] == 1
    assert len(tasks) == 1
    assert tasks[0]["id"] == 2

    # Test deleting non-existent task raises ValueError
    with pytest.raises(ValueError):
        delete_task(tasks, 999)


def test_complete_task():
    tasks = [{"id": 1, "title": "Task 1", "completed": False}]
    completed = complete_task(tasks, 1)
    assert completed["completed"] is True
    assert tasks[0]["completed"] is True

    # Test completing non-existent task raises ValueError
    with pytest.raises(ValueError):
        complete_task(tasks, 999)


def test_file_persistence(pyt_temp_file):
    tasks = []
    add_task(tasks, "Persistent Task")
    save_tasks(tasks, pyt_temp_file)

    loaded_tasks = load_tasks(pyt_temp_file)
    assert len(loaded_tasks) == 1
    assert loaded_tasks[0]["title"] == "Persistent Task"


def test_load_nonexistent_file():
    loaded = load_tasks("nonexistent_file_abc123.json")
    assert loaded == []
