import traceback
import collections
import queue
import threading

from taskon.common import TaskStatus
from taskon.common import taskonAssert
from taskon.abstract_task_processor import AbstractTaskProcessor

class FiniteThreadTaskProcessor(AbstractTaskProcessor):
    def __init__(self, num_threads):
        taskonAssert(num_threads > 0, "num_threads should be positive number")
        self.num_threads = num_threads
        self.threads = None

    def process(self, task, on_complete_callback, *args, **kwargs):
        if self.threads is None:
            self.__startQueueConsumers()
        taskonAssert(self.threads is not None, "TaskProcessor closed")
        task_info = (task, on_complete_callback, args, kwargs)
        if len(self.available_queues) > 0:
            self.__allocate(task_info)
        else:
            waiting_queue.add(task_info)

    def onComplete(self, task):
        """
        On the aknowledgement that @task has completed, we check @waiting_queue
        to see if there are tasks waiting to be assigned.
        """
        allocated_on = self.allocated_on_map.pop(task.id)
        self.available_queues.add(allocated_on)
        if len(self.waiting_queue) > 0:
            self.__allocate(self.waiting_queue.popleft())

    def close(self):
        """
        Terminate all the threads. Wait if these threads are still executing
        any task.
        """
        if self.threads is None:
            return
        for i in range(self.num_threads):
            self.queues[i].put(None)
        for i in range(self.num_threads):
            self.threads[i].join()
        self.threads = None

    def __allocate(self, task_info):
        """Assumes(len(self.available_queues) > 0)"""
        available_queue = self.available_queues.pop()
        task = task_info[0]
        self.allocated_on_map[task.id] = available_queue
        self.queues[available_queue].put(task_info)

    def __startQueueConsumers(self):
        self.available_queues = set(range(self.num_threads))
        self.threads = []
        self.waiting_queue = collections.deque()
        self.allocated_on_map = dict()
        self.queues = list(queue.Queue() for i in range(self.num_threads))
        for qid in range(self.num_threads):
            new_thread = threading.Thread(
                target = self.__queueConsumer,
                args = (self.queues[qid],),
                daemon=True)
            new_thread.start()
            self.threads.append(new_thread)

    def __queueConsumer(self, queue_object):
      while True:
        task_info = queue_object.get()
        if task_info is None:
          break
        (task, on_complete_callback, args, kwargs) = task_info
        try:
            task.setResult(task.run(*args, **kwargs))
            on_complete_callback(task, TaskStatus.SUCCESS)
        except Exception as e:
            task.setError(traceback.format_exc())
            on_complete_callback(task, TaskStatus.FAILURE)

