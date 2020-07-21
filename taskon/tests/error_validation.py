import unittest

from taskon.common import taskonAssert
from taskon.common import TaskonFatalError, TaskonError, taskonAssert
from taskon import SimpleTask
from taskon import TaskResult
from taskon import FiniteThreadTaskProcessor
from taskon import TaskRunner
from taskon import AbortableTask
from taskon import AbstractTaskProcessor

from taskon.utils import runCommand

import taskon.tests.sample_tasks as sample_tasks

class ErrorValidationTest(unittest.TestCase):
    def setUp(self):
        self.task_processor = FiniteThreadTaskProcessor(num_threads=5)

    def test_CyclicDependencyError(self):
        t1 = SimpleTask(
            name="make_money",
            action = sample_tasks.makeMoney,
            args=(TaskResult("make_sandwitch"),))
        t2 = SimpleTask(
            name="make_sandwitch",
            action = sample_tasks.makeSandwitch,
            args=(TaskResult("make_bread"), TaskResult("buy_onion"), 10))
        t3 = SimpleTask(
            name="buy_onion",
            action = sample_tasks.buyGoodOnion,
            args=(TaskResult("make_money"),))
        t4 = SimpleTask(
            name="make_bread", action=sample_tasks.makeBread, args=("flour",))
        with self.assertRaises(TaskonFatalError) as context:
            task_runner = TaskRunner(tasks = [t1, t2, t3, t4],
                                     target_tasks = [t1],
                                     task_processor=self.task_processor)
        expected_error = "Cyclic dependency in tasks: make_money -> "\
                         "make_sandwitch -> buy_onion -> make_money"
        self.assertTrue(expected_error in str(context.exception))

    def test_SampleTask(self):
        self.assertEqual("Money", sample_tasks.makeMoney("Sandwitch"))
        self.assertEqual("Onion", sample_tasks.buyGoodOnion("Money"))

    def test_InvalidTasks(self):
        action = lambda: None
        with self.assertRaises(TaskonFatalError) as context:
            task_runner = TaskRunner(
                tasks = [SimpleTask("task1", action=action),
                         SimpleTask("task1", action=action)],
                task_processor=self.task_processor)
        error = "Found multiple tasks with name 'task1'"
        self.assertTrue(error in str(context.exception))
        with self.assertRaises(TaskonFatalError) as context:
            task_runner = TaskRunner(
                tasks = [SimpleTask(
                    "task1", action=action, args=(TaskResult("task2"),))],
                task_processor=self.task_processor)
        error = "Invalid task name 'task2' used in the TaskResult of task "\
                "'task1'."
        self.assertEqual(error, str(context.exception))
        t1 = SimpleTask("task1", action=action)
        t2 = SimpleTask("task2", action=action)
        t3 = SimpleTask("task2", action=action)
        with self.assertRaises(TaskonFatalError) as context:
            task_runner = TaskRunner(
                tasks = [t1, t2],
                target_tasks = [t2, t3],
                task_processor=self.task_processor)
        error = "Invalid target task 'task2'. @target_tasks must also be "\
                "present in @tasks"
        self.assertEqual(error, str(context.exception))
        with self.assertRaises(TaskonFatalError) as context:
            task_runner = TaskRunner(
                tasks = [SimpleTask(
                    name="task1", action=action, args=10, kwargs=dict(a=5))],
                task_processor=self.task_processor)
        error = "Task 'task1' have invalid value for args field, it should "\
                "be a tuple."
        self.assertEqual(error, str(context.exception))
        with self.assertRaises(TaskonFatalError) as context:
            task_runner = TaskRunner(
                tasks = [SimpleTask(
                    name="task1", action=action, args=(10,20), kwargs=10)],
                task_processor=self.task_processor)
        error = "Task 'task1' have invalid value for kwargs field, it should "\
                "be a dictionary."
        self.assertEqual(error, str(context.exception))
        task_runner = TaskRunner(
            tasks = [SimpleTask("task1", action=action),
                     SimpleTask("task2", action=action)],
            task_processor=self.task_processor)
        self.assertEqual("task2", task_runner.getTask("task2").name)
        with self.assertRaises(TaskonError) as context:
            task_runner.getTask("task3")
        self.assertEqual("Invalid task 'task3'", str(context.exception))

    def test_CallPureAbstractMethods(self):
        task = AbortableTask("task1")
        with self.assertRaises(TaskonFatalError) as context:
            task.abort()
        error = "Abstract method 'abort' should not be called."
        self.assertEqual(error, str(context.exception))
        task_processor = AbstractTaskProcessor()
        with self.assertRaises(TaskonFatalError) as context:
            task_processor.process(task, lambda t,s: None)
        error = "Purely abstract method 'process' should not be called."
        self.assertEqual(error, str(context.exception))

    def test_RunInvalidCommand(self):
        with self.assertRaises(TaskonError) as context:
            runCommand("ls xgzwtwicppo")
        error = "Command 'ls xgzwtwicppo' failed with error_code 1"
        self.assertEqual(error, str(context.exception))
        # print(str(context.exception))


        # print(str(context.exception))






