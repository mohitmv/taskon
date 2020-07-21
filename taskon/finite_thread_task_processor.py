import traceback
import collections
import queue
import threading

from taskon.common import TaskStatus
from taskon.common import taskonAssert
from taskon.abstract_task_processor import AbstractTaskProcessor

class FiniteThreadTaskProcessor(AbstractTaskProcessor):
    """
    Note: As per the AbstractTaskProcessor contract, all the public APIs
          can choose to be thread unsafe because task schedular guarantees to
          call them in a single thread.
    """
    def __init__(self, num_threads, daemon_thread=True):
        taskonAssert(num_threads > 0, "num_threads should be positive number")
        self.num_threads = num_threads
        self.threads = None
        self.daemon_thread = daemon_thread

    def process(self, task, on_complete_callback, *args, **kwargs):
        """
        Handle the request for execution of a new @task.
        Allocate the task to one of the available queue. If no queue is
        available, push the task in self.waiting_queue.
        """
        if self.threads is None:
            self.__startQueueConsumers()
        task_info = (task, on_complete_callback, args, kwargs)
        if len(self.available_queues) > 0:
            self.__allocate(task_info)
        else:
            self.waiting_queue.append(task_info)

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
        if not self.daemon_thread:
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
                daemon=self.daemon_thread)
            new_thread.start()
            self.threads.append(new_thread)

    def __queueConsumer(self, queue_object):
        """
        Continue to consume and execute tasks from @queue_object forever until
        a 'None' entry is received.
        """
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
