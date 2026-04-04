# server/tasks/__init__.py
from .task_easy import get_random_easy_task, EASY_TASKS
from .task_medium import get_random_medium_task, MEDIUM_TASKS
from .task_hard import get_random_hard_task, HARD_TASKS

__all__ = [
    "get_random_easy_task", "EASY_TASKS",
    "get_random_medium_task", "MEDIUM_TASKS",
    "get_random_hard_task", "HARD_TASKS",
]
