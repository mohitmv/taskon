import queue
import threading
import collections

from taskon.common import TaskonFatalError
from taskon.common import TaskonError
from taskon.common import TaskStatus
from taskon.utils import cycleDetection
from taskon.utils import depsCover
from taskon.scheduling_algorithm import SchedulingAlgorithm

class TaskResultPlaceholderVisitor:
    """
    A helper visitor used in __preprocessTaskArgs. A visitor that is used
    for visiting on TaskResult placeholders used in args/kwargs of a task.
    This visitor:
    1. Populate the task id on the TaskResult obect.
    2. Collect dependency_tasks for a given task.
    """
    def __init__(self, task, task_name_to_task_map):
        self.task = task
        self.task_name_to_task_map = task_name_to_task_map
        self.dependency_tasks = set()

    def __call__(self, task_output):
        if task_output.name not in self.task_name_to_task_map:
            raise TaskonFatalError(
                "Invalid task name '%s' used in the TaskResult of "
                "task '%s'." % (task_output.name, self.task.name))
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
        1. Populate the task.id in TaskResult placeholde.
        2. For each task create a set of dependency tasks by following the
           usage of TaskResult object in inputs of a task.
        """
        self.dependency_graph = dict()
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
            visitor = TaskResultPlaceholderVisitor(task, task_name_to_task_map)
            task.visitTaskResultPlaceholders(visitor)
            self.dependency_graph[task_id] = visitor.dependency_tasks

    def __preprocessDependencyGraph(self):
        """
        1. Populate the @self.effective_tasks. Effective target tasks is
           the dependency cover of target_tasks. In some cases
           effective_tasks might be less than overall tasks.
        2. Ensure that there is no cyclic dependency among the tasks.
        """
        nodes = self.target_tasks
        edge_func = lambda task_id: self.dependency_graph[task_id]
        cycle_detection = cycleDetection(nodes, edge_func)
        if cycle_detection.cycle_found:
            cycle_path = list(self.tasks_map[i].name
                                 for i in cycle_detection.cycle_path)
            error = TaskonFatalError(
                "Cyclic dependency in tasks: " + (" -> ".join(cycle_path)))
            error.cycle_path = cycle_path
            raise error
        self.effective_tasks = depsCover(nodes, edge_func)

    def __getTaskInputs(self, task):
        """
        Return the real inputs of a given tasks by replacing the TaskResult
        placeholder with actual output of the referenced task.
        """
        args, kwargs = task.visitTaskResultPlaceholders(
            lambda task_output: self.tasks_map[task_output.id].getResult())
        return args, kwargs

    def __resetTasks(self):
        """Reset all the tasks"""
        for i, task in self.tasks_map.items():
            task.reset()

    def run(self, continue_on_failure=False):
        deps_func = lambda task_id: self.dependency_graph[task_id]
        task_inputs_func = self.__getTaskInputs
        self.__resetTasks()
        scheduling_algorithm = SchedulingAlgorithm(
            self.task_processor, task_inputs_func, self.tasks_map, deps_func)
        scheduling_algorithm.run(self.effective_tasks, continue_on_failure)
        self.failed_tasks = []
        self.succeeded_tasks = []
        self.skipped_tasks = []
        for task_id in self.effective_tasks:
            task = self.tasks_map[task_id]
            if task.status == TaskStatus.SUCCESS:
                self.succeeded_tasks.append(task)
            elif task.status == TaskStatus.SKIPPED:
                self.skipped_tasks.append(task)
            else:
                self.failed_tasks.append(task)

    def getTask(self, task_name):
        if task_name not in self.task_name_to_task_map:
            raise TaskonError("Invalid task '%s'" % task_name)
        return self.task_name_to_task_map[task_name]

    def getSuccessSummaryString(self):
        lines = []
        num_all = len(self.effective_tasks)
        num_s = len(self.succeeded_tasks)
        num_f = len(self.failed_tasks)
        num_skip = len(self.skipped_tasks)
        info = [(num_s, "succeeded"), (num_f, "failed"), (num_skip, "skipped")]
        for num, name in info:
            if num > 0:
                lines.append("%s/%s tasks %s." % (num, num_all, name))
        for i in self.effective_tasks:
            task = self.tasks_map[i]
            lines.append(" %s : %s" % (task.name, task.getStatus().name))
        return "\n".join(lines) + "\n"

    def printSuccessSummary(self):
        print(self.getSuccessSummaryString())

    def getErrorSummaryString(self):
        output = ""
        for task in self.failed_tasks:
            output += task.name + ":\n"
            output += task.getError() + "\n"
            output += "-"*20
        if len(self.failed_tasks) == 0:
            output += "No failed task."
        return output

    def printErrorSummary(self):
        print(self.getErrorSummaryString())
