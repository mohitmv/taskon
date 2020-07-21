import queue

from taskon.common import TaskStatus

class SchedulingAlgorithm:
    """
    An implementation of task scheduling algorithm.
    Algorithm:
    Step-1: Find all the tasks with no dependencies and schedule them for
            execution. Task processor will execute it as soon as possible.
    Step-2: Wait for the completion status of scheduled tasks:
            On completion of a scheduled task T:
                If the execution of task T failed:
                    Ignore if 'continue_on_failure' is chosen else Stop.
                Else
                    for each task P dependent on T:
                        Remove the dependency relation P -> T
                        If the task P still depends on other tasks - ignore.
                        else: schedule the task P for execution.
    Step-3: We reached at step 3 either because execution of all scheduled
           tasks completed or the execution of a task failed. If there are
           still pending tasks then abort them.
    Step-4: Calculate the skipped tasks and return.
    """
    def __init__(self, task_processor, task_inputs_func, tasks_map, deps_func):
        self.task_processor = task_processor
        self.task_inputs_func = task_inputs_func
        self.tasks_map = tasks_map
        self.deps_func = deps_func

    def __createRuntimeGraph(self, effective_tasks, deps_func):
        incoming_edges = dict((i, set(deps_func(i))) for i in effective_tasks)
        outgoing_edges = dict((i, []) for i in effective_tasks)
        for i, deps in incoming_edges.items():
            for d in deps:
                outgoing_edges[d].append(i)
        return incoming_edges, outgoing_edges

    def __processTask(self, task):
        """
        Process the execution of @task in task_processor. This @task can be
        executed by anytime now. At this point all the dependency tasks of the
        @task have executed successfully, hence we can use 'task_inputs_func'
        to get the real inputs of @task.
        """
        args, kwargs = self.task_inputs_func(task)
        self.tasks_in_progress.add(task.id)
        self.task_processor.process(
            task, self.__onCompleteCallback, *args, **kwargs)

    def __onCompleteCallback(self, task, status):
        """
        A callback to be called by task_processor after the completion of a
        scheduled task.
        """
        self.completion_updates_queue.put((task, status))

    def run(self, effective_tasks, continue_on_failure=False):
        """The main scheduling algorithm."""
        self.completion_updates_queue = queue.Queue()
        self.tasks_in_progress = set()
        incoming_edges, outgoing_edges = self.__createRuntimeGraph(
            effective_tasks, self.deps_func)
        for task_id in effective_tasks:
            if len(incoming_edges[task_id]) == 0:
                self.__processTask(self.tasks_map[task_id])
        while len(self.tasks_in_progress) > 0:
            task, status = self.completion_updates_queue.get() # Blocking step.
            task.status = status
            self.task_processor.onComplete(task)
            self.tasks_in_progress.remove(task.id)
            if task.status != TaskStatus.SUCCESS:
                task_name = self.tasks[task_id].name
                if self.continue_on_failure:
                    continue
                else:
                    break
            for d_task_id in outgoing_edges[task.id]:
                incoming_edges[d_task_id].remove(task.id)
                if len(incoming_edges[d_task_id]) == 0:
                    self.__processTask(self.tasks_map[d_task_id])
        for task_id in self.tasks_in_progress:
            self.tasks_map[task_id].abort()
        self.task_processor.close()

