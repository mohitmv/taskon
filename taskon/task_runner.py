import queue
import threading
import collections

from taskon.utils import TaskonFatalError
from taskon.utils import cycleDetection
from taskon.utils import depsCover
from taskon.utils import TaskStatus

class TaskResultPlaceholderVisitor:
    """
    A helper visitor used in __preprocessTaskArgs. A visitor that is used
    for visiting on TaskResult placeholders used in args/kwargs of a task.
    This visitor:
    1. Populate the task id on the TaskResult obect.
    2. Collect dependency_tasks for a given task.
    """
    def __init__(self, task_name_to_task_map):
        self.task_name_to_task_map = task_name_to_task_map
        self.dependency_tasks = set()

    def __call__(self, task_output):
        if task_output.name not in self.task_name_to_task_map:
            raise TaskonFatalError(
                "Invalid  task name '%s' used in the TaskResult of "
                "task '%s'." % (j, task.name))
        task_output.id = self.task_name_to_task_map[task_output.name].id
        self.dependency_tasks.add(task_output.id)
        return task_output


class TaskRunner:
    def __init__(self, tasks, task_processor, target_tasks=None):
        self.task_processor = task_processor
        self.__preprocessTasks(tasks, target_tasks or tasks)

    def __preprocessTasks(self, tasks, target_tasks):
        """
        1. Assign a unique integer id to each task. All the references to
           a tasks should also reference it by it's unique integer id instead
           of task name.
        2. Populate
            a). @self.tasks_map - an ordered map from task_id -> task
            b). @self.task_name_to_task_map - a map from task_name -> task.
            c). @self.target_tasks - ids of target tasks.
        3. Validate cyclic dependencies among tasks.
        """
        self.__populateTaskIds(tasks, target_tasks)
        self.__preprocessTaskArgs(self.tasks_map, self.task_name_to_task_map)
        self.__preprocessDependencyGraph()

    def __populateTaskIds(self, tasks, target_tasks):
        """
        Assign a unique integer id to each task and popluate @self.tasks_map,
        @self.task_name_to_task_map and @self.target_tasks, required for #2 in
        __preprocessTasks method.
        """
        self.tasks_map = collections.OrderedDict()
        self.task_name_to_task_map = {}
        for index, task in enumerate(tasks):
            task.id = index
            self.tasks_map[index] = task
            if task.name in self.task_name_to_task_map:
                raise TaskonFatalError(
                    "Found multiple tasks with name '%s'. Task name is a "
                    "unique identity of a task. It should be unique across all "
                    "tasks. " % task.name)
            self.task_name_to_task_map[task.name] = task
        for task in target_tasks:
            if task.id is None or task.id not in self.tasks_map:
                raise TaskonFatalError(
                    "Invalid target task '%s'. @target_tasks must also be "
                    "present in @tasks" % task.name)
        self.target_tasks = set(task.id for task in target_tasks)

    def __preprocessTaskArgs(self, tasks, task_name_to_task_map):
        """
        Assume:
        1. task.id is populated for each task in @tasks.

        Do:
        1. For each task create a set of dependency tasks by following the
           usage of TaskResult object in inputs of a task.
        2. Populate the task.id in TaskResult object.
        """
        for task_id, task in tasks.items():
            dependency_tasks = []
            if not isinstance(task.args, tuple):
                raise TaskonFatalError(
                    "Task '%s' have invalid value for args field, it should be "
                    "a tuple." % task.name)
            if not isinstance(task.kwargs, dict):
                raise TaskonFatalError(
                    "Task '%s' have invalid value for kwargs field, it should "
                    "be a dictionary." % task.name)
            visitor = TaskResultPlaceholderVisitor(task_name_to_task_map)
            task.visitTaskResultPlaceholders(visitor)
            task.dependency_tasks = visitor.dependency_tasks

    def __preprocessDependencyGraph(self):
        """
        1. Populate the @self.effective_tasks. Effective target tasks is
           the dependency cover of target_tasks. In some cases
           effective_tasks might be less than overall tasks.
        2. Ensure that there is no cyclic dependency among the tasks.
        """
        nodes = self.target_tasks
        edge_func = lambda task_id: self.tasks_map[task_id].dependency_tasks
        cycle_detection = cycleDetection(nodes, edge_func)
        if cycle_detection.cycle_found:
            cycle_path = list(self.tasks_map[i].name
                                 for i in cycle_detection.cycle_path)
            error = TaskonFatalError(
                TaskonException.CYCLIC_DEPENDENCY_FOUND,
                "Cyclic dependency in tasks: " + (" -> ".join(cycle_path)))
            error.cycle_path = cycle_path
            raise error
        self.effective_tasks = depsCover(nodes, edge_func)

    def __populateRuntimeGraph(self):
        incoming_edges = dict((tid, set(self.tasks_map[tid].dependency_tasks))
                                 for tid in self.effective_tasks)
        outgoing_edges = dict((i, []) for i in self.effective_tasks)
        for i, deps in incoming_edges.items():
            for d in deps:
                outgoing_edges[d].append(i)
        return incoming_edges, outgoing_edges

    def __processTask(self, task):
        """
        1. Replace the TaskResult placeholder with actual output of other task
           in the args/kwargs of @task.
        2. Process the execution of @task in @self.task_processor. This @task
           can be executed by @self.task_processor anytime now. At this point
           all the dependency tasks of the @task have executed successfully.
        """
        args, kwargs = task.visitTaskResultPlaceholders(
            lambda task_output: self.tasks_map[task_output.id].getResult())
        self.tasks_in_progress.add(task.id)
        self.task_processor.process(
            task, self.__onCompleteCallback, *args, **kwargs)

    def __onCompleteCallback(self, task, status):
        self.task_completion_updates_queue.put((task, status))

    def __getSkippedTasks(self):
        """
        Get the list of skipped tasks.
        Skipped tasks = All effective tasks - failed tasks - succeeded_tasks
        """
        non_skipped_tasks = self.failed_tasks + self.succeeded_tasks
        non_skipped_task_ids = set(task.id for task in non_skipped_tasks)
        skipped_task_ids = self.effective_tasks - non_skipped_task_ids
        skipped_tasks = set(self.tasks_map[i] for i in skipped_task_ids)
        return skipped_tasks

    def run(self):
        """Execute the tasks."""
        self.task_completion_updates_queue = queue.Queue()
        self.tasks_in_progress = set()
        self.failed_tasks = []
        self.succeeded_tasks = []
        (incoming_edges, outgoing_edges) = self.__populateRuntimeGraph()
        for task_id in self.effective_tasks:
            if len(incoming_edges[task_id]) == 0:
                self.__processTask(self.tasks_map[task_id])
        while len(self.tasks_in_progress) > 0:
            task, status = self.task_completion_updates_queue.get()
            task.status = status
            self.task_processor.onComplete(task, status)
            self.tasks_in_progress.remove(task.id)
            if status != TaskStatus.SUCCESS:
                task_name = self.tasks[task_id].name
                self.failed_tasks.append(task)
                if self.continue_on_failure:
                    continue
                else:
                    break
            for d_task_id in outgoing_edges[task.id]:
                self.succeeded_tasks.append(task)
                incoming_edges[d_task_id].remove(task.id)
                if len(incoming_edges[d_task_id]) == 0:
                    self.__processTask(self.tasks_map[d_task_id])
        for task_id in self.tasks_in_progress:
            self.tasks_map[task_id].abort()
        self.skipped_tasks = self.__getSkippedTasks()

    def getTask(self, task_name):
        if task_name not in self.task_name_to_task_map:
            raise TaskonError("Invalid task '%s'" % task_name)
        return self.task_name_to_task_map[task_name]

