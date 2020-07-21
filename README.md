# Taskon

Taskon is a task runner used for execution of interdependnt tasks. When some tasks are dependent on the results of other tasks and they form a complex dependency graph, `taskon` can be used for efficient scheduling for the execution of given tasks.

## Why taskon
1. Design of `Taskon` is dead simple at the core.
2. Taskon is super easy to use, hackable to the core and yet powerful to schedule **billions** of the interdependnt tasks very efficiently, leveraging the available compute resources in best possible way.
3. All the components of `Taskon` are abstract and supports in-drop replacement. You can bring even more efficient implementation of a component for your use case and replace it. Taskon comes with a default implementations of these components which are pretty efficient. Since the design of `Taskon` is dead simple, you can make use of Taskon's default components and build your own task runner.
4. Scheduling algorithm used in taskon is very efficult and dead simple to implement.
5. Scheduling algorithm use a TaskProcessor abstraction for the execute of a single task. A custom and arbitrary powerful implementation of TaskProcessor can be integrated with taskon scheduler to enable you to execute your tasks on a single thread, parallel threads, multiple processors, multiple remote machines, mobile devices, quantum machines or any other way of computing you can imagine.
6. Taskon is very fast simply because it does't do any magic internally. Taskon is transparent to the core.
7. Taskon is heavily tested with 100% code coverage. `Taskon` is tested with 1 million sample tasks in dependency graphs.

## How to use

```python
from taskon import SimpleTask, TaskResult, TaskRunner, TaskStatus
from taskon import FiniteThreadTaskProcessor

def MakeSandwitch(bread, onion, grill_duration):
  print("Cutting " + onion)
  print("Grilling " + bread + " for " + str(grill_duration) + " minutes")
  return onion + "-Sandwitch"

def MakeBread(flour):
  print("Processing " + flour)
  return "Bread"

def BuyOnion():
  return "Onion"


t1 = SimpleTask(name = "make_bread", action = MakeBread, args=("flour",))

t2 = SimpleTask(name = "make_sandwitch",
                action = MakeSandwitch,
                args = (TaskResult("make_bread"), TaskResult("buy_onion"), 4))

t3 = SimpleTask(name = "buy_onion", action = BuyOnion)

task_processor = FiniteThreadTaskProcessor(num_threads=6)
task_runner = TaskRunner(tasks = [t1, t2, t3],
                         target_tasks = [t2],
                         task_processor = task_processor)

task_runner.run()

assert task_runner.getTask("make_sandwitch").getStatus() == TaskStatus.SUCCESS
assert task_runner.getTask("make_sandwitch").getResult() == "Onion-Sandwitch"

```

# API documentation

The taskon module defines the following classes and exceptions:

Classes/Exceptions                    | Documentation
------------------------------------- | ------------------------
`taskon.AbstractTask`                 | An abstract task. All tasks must derive from `Task`
`taskon.SimpleTask`                   | A simple implementation of task.
`taskon.AbortableTask`                | An abstract interface for the tasks which can be aborted.
`taskon.BashCommandTask`              | A task to run bash command, derived from AbortableTask.
`taskon.TaskResult`                   | Placeholder to represent result of another task.
[`taskon.AbstractTaskProcessor`](taskon/abstract_task_processor.py) | An abstract way to process tasks.
`taskon.NaiveTaskProcessor`           | Naive task processor (single threaded). Designed for the demonstration of AbstractTaskProcessor. Should not be used practically.
[`taskon.FiniteThreadTaskProcessor`](taskon/finite_thread_task_processor.py)    | N threaded Queue based task processor.
[`taskon.InfiniteThreadTaskProcessor`](taskon/infinite_thread_task_processor.py)  | Unbounded threaded task processor.
`taskon.RemoteExecutionTaskProcessor` | Task processor that execute bash commands in remote machines.
`taskon.TaskRunner`                   | Implements task scheduling algorithm.


# Coverage

![Test Coverage](docs/coverage.png)

# Scheduling Algorithm

An implementation of default task scheduling algorithm

```

Step-1: Find all the tasks with no dependencies and schedule them in task
        processor for execution. Task processor will execute it as soon as
        possible.

Step-2: Wait for the completion status of scheduled tasks:
        On completion of a scheduled task T:
            If the execution of task T failed:
                Stop if 'continue_on_failure' flag is False else do nothing.
            Else
                for each task P dependent on T:
                    Remove the dependency relation P -> T
                    If the task P still depends on other tasks - ignore.
                    else: schedule the task P for execution.

Step-3: We reached at step 3 either because execution of all scheduled
       tasks completed or the execution of some task failed. If there are
       still pending tasks then abort them.

Step-4: We are done.

```
Take a look at the [implementation of scheduler](taskon/scheduling_algorithm.py).

# Task Processors

1. The contract of task processor is defined [here](taskon/abstract_task_processor.py).
2. FiniteThreadTaskProcessor is one the implementation of task processor. It maintains N threads. When a task is scheduled in FiniteThreadTaskProcessor, it will attempt to execute it immediately if there are ideal threads, otherwise it will store the task in a queue, to be executed whenever a thread becomes available.
3. InfiniteThreadTaskProcessor is another implementation of task processor. It create a new thread whenever it receive the request for execution of a task.
