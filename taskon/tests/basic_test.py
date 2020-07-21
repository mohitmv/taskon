import unittest
import re
from parameterized import parameterized

from taskon import SimpleTask, TaskResult, TaskRunner, TaskStatus
from taskon import BashCommandTask
from taskon import NaiveTaskProcessor, FiniteThreadTaskProcessor
from taskon import InfiniteThreadTaskProcessor

from taskon.tests.test_utils import readFile
import taskon.tests.sample_tasks as sample_tasks


def getTestParameters():
    return [
        ["naive_task_processor", NaiveTaskProcessor()],
        ["finite_thread_task_processor",
         FiniteThreadTaskProcessor(num_threads=4)],
        ["infinite_thread_task_processor", InfiniteThreadTaskProcessor()]]


class TaskonBasicTest(unittest.TestCase):
    @parameterized.expand(getTestParameters())
    def test_main(self, name, task_processor):
        t1 = SimpleTask(name = "make_sandwitch",
                        action = sample_tasks.makeSandwitch,
                        args = (TaskResult("make_bread"),
                                TaskResult("buy_onion"), 4))

        t2 = SimpleTask(name="make_bread", action=sample_tasks.makeBread, args=("flour",))

        t3 = SimpleTask(name="buy_onion", action=sample_tasks.buyOnion)

        task_runner = TaskRunner(tasks = [t1, t2, t3],
                                 target_tasks = [t1],
                                 task_processor = task_processor)
        task_runner.run()

        self.assertEqual(TaskStatus.SUCCESS,
                         task_runner.getTask("make_sandwitch").getStatus())
        self.assertEqual("Onion-Sandwitch",
                         task_runner.getTask("make_sandwitch").getResult())


class TaskonBasicErrorTest(unittest.TestCase):
    @parameterized.expand(getTestParameters())
    def test_error_case(self, name, task_processor):
        t1 = SimpleTask(name = "make_sandwitch",
                        action = sample_tasks.makeSandwitch,
                        args = (TaskResult("make_bread"),
                                TaskResult("buy_onion"), 4))
        t2 = SimpleTask(
            name="make_bread",
            action=sample_tasks.makeFaultyBread,
            args=("flour",))
        t3 = SimpleTask(name="buy_onion", action=sample_tasks.buyOnion)

        task_runner = TaskRunner(tasks = [t1, t2, t3],
                                 target_tasks = [t1],
                                 task_processor = task_processor)
        task_runner.run(continue_on_failure=True)
        self.assertEqual(TaskStatus.FAILURE,
                         task_runner.getTask("make_bread").getStatus())
        e_error1 = 'ZeroDivisionError: division by zero'
        e_error2 = 'sample_tasks.py", line [0-9]+, in makeFaultyBread'
        o_error = task_runner.getTask("make_bread").getError()
        self.assertTrue(e_error1 in task_runner.getErrorSummaryString())


        self.assertTrue(e_error1 in o_error)
        self.assertTrue(re.search(e_error2, o_error) is not None, o_error)

        self.assertEqual(TaskStatus.SUCCESS,
                         task_runner.getTask("buy_onion").getStatus())
        self.assertEqual("Onion",
                         task_runner.getTask("buy_onion").getResult())

        self.assertEqual(TaskStatus.SKIPPED,
                         task_runner.getTask("make_sandwitch").getStatus())

        name_list = lambda task_list: list(x.name for x in task_list)
        self.assertEqual(["make_bread"], name_list(task_runner.failed_tasks))
        self.assertEqual(["buy_onion"], name_list(task_runner.succeeded_tasks))
        self.assertEqual(["make_sandwitch"],
                         name_list(task_runner.skipped_tasks))


class ContinueOnFailureTest(unittest.TestCase):
    def test_error_case(self):
        t1 = SimpleTask(name = "make_sandwitch",
                        action = sample_tasks.makeCheeseSandwitch,
                        args = (TaskResult("make_bread"),
                                TaskResult("buy_cheese"),
                                TaskResult("buy_onion"), 4))
        t2 = SimpleTask(name="make_bread", action=sample_tasks.makeFaultyBreadSleep1, args=("flour",))
        t3 = SimpleTask(name="buy_onion", action=sample_tasks.buyOnionSleep2)
        t4 = SimpleTask(name="buy_cheese", action=sample_tasks.buyCheese)
        task_processor = FiniteThreadTaskProcessor(num_threads=5)
        task_runner = TaskRunner(tasks = [t1, t2, t3, t4],
                                 target_tasks = [t1],
                                 task_processor = task_processor)
        task_runner.run()
        self.assertEqual(TaskStatus.FAILURE,
                         task_runner.getTask("make_bread").getStatus())
        e_error1 = 'ZeroDivisionError: division by zero'
        e_error2 = 'sample_tasks.py", line [0-9]+, in makeFaultyBread'
        o_error = task_runner.getTask("make_bread").getError()
        self.assertTrue(e_error1 in o_error)
        self.assertTrue(re.search(e_error2, o_error) is not None, o_error)

        self.assertEqual(TaskStatus.SUCCESS,
                         task_runner.getTask("buy_cheese").getStatus())
        self.assertEqual("Cheese",
                         task_runner.getTask("buy_cheese").getResult())

        self.assertEqual(TaskStatus.SKIPPED,
                         task_runner.getTask("buy_onion").getStatus())

        self.assertEqual(TaskStatus.SKIPPED,
                         task_runner.getTask("make_sandwitch").getStatus())

        name_list = lambda task_list: list(x.name for x in task_list)
        self.assertEqual(["make_bread"], name_list(task_runner.failed_tasks))
        self.assertEqual(["buy_cheese"], name_list(task_runner.succeeded_tasks))
        self.assertEqual(["make_sandwitch", "buy_onion"],
                         name_list(task_runner.skipped_tasks))

        task_runner.run(continue_on_failure=True)
        self.assertEqual(["make_bread"], name_list(task_runner.failed_tasks))
        self.assertEqual(set(["buy_cheese", "buy_onion"]),
                         set(name_list(task_runner.succeeded_tasks)))
        self.assertEqual(["make_sandwitch"],
                         name_list(task_runner.skipped_tasks))
        self.assertEqual("Onion",
                         task_runner.getTask("buy_onion").getResult())

class BashCommandTest(unittest.TestCase):
    def test_basic(self):
        output_file = "/tmp/taskon_sandwitch.txt"
        cheese_file = "/tmp/taskon_cheese.txt"
        t1 = BashCommandTask(
            name="make_sandwitch",
            command = lambda onion: "echo %s > %s" % (onion, output_file),
            args=(TaskResult("buy_onion"),))
        t2 = SimpleTask(
            name="buy_onion",
            action = lambda: "Onion")
        t3 = SimpleTask(
            name="make_cheese_sandwitch",
            action = sample_tasks.makeCheeseSandwitch,
            args=("bread", "cheese", "onion", 18))
        t4 = BashCommandTask(
            name="buy_cheese",
            command = "echo Cheese > %s" % cheese_file)
        task_processor = FiniteThreadTaskProcessor(num_threads=5)
        task_runner = TaskRunner(tasks = [t1, t2, t3, t4],
                                 target_tasks = [t1, t3, t4],
                                 task_processor=task_processor)
        task_runner.run()
        task_runner.printSuccessSummary()
        task_runner.printErrorSummary()
        self.assertEqual(4, len(task_runner.succeeded_tasks))
        self.assertEqual("Onion\n", readFile(output_file))
        self.assertEqual("Cheese\n", readFile(cheese_file))
        for task in task_runner.succeeded_tasks:
            self.assertEqual(TaskStatus.SUCCESS, task.getStatus())
