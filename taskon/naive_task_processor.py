import traceback

from taskon.common import TaskStatus
from taskon.abstract_task_processor import AbstractTaskProcessor

class NaiveTaskProcessor(AbstractTaskProcessor):
    def process(self, task, on_complete_callback, *args, **kwargs):
        try:
            task.setResult(task.run(*args, **kwargs))
            on_complete_callback(task, TaskStatus.SUCCESS)
        except Exception:
            task.setError(traceback.format_exc())
            on_complete_callback(task, TaskStatus.FAILURE)
