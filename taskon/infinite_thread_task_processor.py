import traceback
import collections
import queue
import threading

from taskon.common import TaskStatus
from taskon.common import taskonAssert
from taskon.abstract_task_processor import AbstractTaskProcessor

class InfiniteThreadTaskProcessor(AbstractTaskProcessor):
    def __init__(self):
        self.threads_map = dict()

    def process(self, task, on_complete_callback, *args, **kwargs):
        new_thread = threading.Thread(
            target = self.__runTask,
            args = (task, on_complete_callback, args, kwargs),
            daemon=True)
        new_thread.start()
        self.threads_map[task.id] = new_thread

    def onComplete(self, task):
        thread = self.threads_map.pop(task.id)
        thread.join()

    def __runTask(self, task, on_complete_callback, args, kwargs):
        try:
            task.setResult(task.run(*args, **kwargs))
            on_complete_callback(task, TaskStatus.SUCCESS)
        except Exception as e:
            task.setError(traceback.format_exc())
            on_complete_callback(task, TaskStatus.FAILURE)
