import unittest
import time

from taskon import SimpleTask
from taskon import TaskResult
from taskon import TaskRunner
from taskon import FiniteThreadTaskProcessor
from taskon import TaskStatus
from taskon import BashCommandTask

class FiniteThreadTaskProcessorTest(unittest.TestCase):
    def test_basic(self):
        mul2 = lambda x: (time.sleep(1), x*2)[-1]
        sum_n = lambda *args: (time.sleep(0.1), sum(args))[-1]
        sum_n_plus_x = lambda *args, x=10: (time.sleep(1), sum(args) + x)[-1]
        t1 = SimpleTask("task1", action=mul2, args=(10,))
        t2 = SimpleTask("task2", action=mul2, args=(20,))
        t3 = SimpleTask("task3", action=mul2, args=(30,))
        t4 = SimpleTask("task4", action=mul2, args=(40,))
        t5 = SimpleTask("task5", action=mul2, args=(50,))
        t6 = SimpleTask(
            "task6", action=sum_n, args=(
                TaskResult("task1"),
                TaskResult("task2"),
                TaskResult("task3"),
                TaskResult("task5")))
        t7 = SimpleTask(
            "task7", action=sum_n_plus_x, args=(
                TaskResult("task1"),
                TaskResult("task5")),
            kwargs=dict(x=100))
        t8 = SimpleTask(
            "task8", action=sum_n_plus_x, args=(
                TaskResult("task3"),
                TaskResult("task6"),
                TaskResult("task5")))
        task_processor = FiniteThreadTaskProcessor(
            num_threads=2, daemon_thread=False)
        task_runner = TaskRunner(
            tasks=[t1, t2, t3, t4, t5, t6, t7, t8],
            target_tasks=[t7, t8],
            task_processor=task_processor)
        task_runner.run()
        task_runner.printSuccessSummary()
        task_runner.printErrorSummary()
        self.assertEqual(220, task_runner.getTask("task7").getResult())
        self.assertEqual(390, task_runner.getTask("task8").getResult())
        task_processor.close()

    def test_error_case(self):
        mul2 = lambda x: (time.sleep(1), x*2)[-1]
        sum_n = lambda *args: (time.sleep(0.2), sum(args))[-1]
        sum_n_plus_x = lambda *args, x=10: (time.sleep(1), sum(args) + x)[-1]
        t0 = SimpleTask("task0", action=lambda x: x*2, args=(5,))
        t1 = SimpleTask("task1", action=mul2, args=(10,))
        t2 = BashCommandTask("task2", command = "sleep 20s", result=40)
        t3 = SimpleTask("task3", action=mul2, args=(30,))
        t4 = SimpleTask(
            name = "task4",
            action=lambda x: (time.sleep(0.5), 1/0),
            args=(TaskResult("task0"),))
        t5 = SimpleTask("task5", action=mul2, args=(50,))
        t6 = SimpleTask(
            "task6", action=sum_n, args=(
                TaskResult("task1"),
                TaskResult("task2"),
                TaskResult("task5")))
        t7 = SimpleTask(
            "task7", action=sum_n_plus_x, args=(
                TaskResult("task1"),
                TaskResult("task5")),
            kwargs=dict(x=100))
        t8 = SimpleTask(
            "task8", action=sum_n_plus_x, args=(
                TaskResult("task2"),
                TaskResult("task6"),
                TaskResult("task4"),
                TaskResult("task5")))
        task_processor = FiniteThreadTaskProcessor(num_threads=10)
        task_runner = TaskRunner(
            tasks=[t0, t1, t2, t3, t4, t5, t6, t7, t8],
            target_tasks=[t7, t8],
            task_processor=task_processor)
        task_runner.run()
        self.assertEqual(
            TaskStatus.SUCCESS, task_runner.getTask("task0").getStatus())
        self.assertEqual(10, task_runner.getTask("task0").getResult())
        self.assertEqual(
            TaskStatus.FAILURE, task_runner.getTask("task4").getStatus())
        error = "ZeroDivisionError: division by zero"
        self.assertTrue(error in task_runner.getTask("task4").getError())
        self.assertEqual(
            TaskStatus.SKIPPED, task_runner.getTask("task8").getStatus())


