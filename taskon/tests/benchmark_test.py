import unittest
import time
import random

from taskon import SimpleTask
from taskon import TaskResult
from taskon import TaskRunner
from taskon import FiniteThreadTaskProcessor
from taskon import TaskStatus
from taskon import BashCommandTask

def TaskType1(*args):
    return max(args)

def TaskType2(a, b):
    return a - b

def TaskType3(a, b):
    return min(a, b)

class BenchmarkTest(unittest.TestCase):
    def test_basic(self):
        num_tasks = 100000
        tasks = []
        task_types = [TaskType1, TaskType2, TaskType3]
        time0 = time.time()
        for i in range(num_tasks):
            p = random.randint(0, 10)
            r = p % 3
            if i < 5:
                args = (i, i*p, p) if r == 0 else (i, i*2)
            else:
                r0 = random.randint(0, i-1)
                r1 = random.randint(0, i-1)
                if r == 0:
                    args = (i, TaskResult(r0), TaskResult(r1))
                else:
                    args = (TaskResult(r0), TaskResult(r1))
            tasks.append(SimpleTask(name=i, action=task_types[r], args=args))
        time1 = time.time()
        task_processor = FiniteThreadTaskProcessor(num_threads=5)
        task_runner = TaskRunner(
            tasks=tasks,
            target_tasks=tasks,
            task_processor=task_processor)
        task_runner.run()
        time2 = time.time()
        print("Successful tasks = ", len(task_runner.succeeded_tasks))
        print("Time taken = ", (time2 - time1), " seconds")

