from taskon import SimpleTask, TaskResult, TaskRunner, TaskStatus
from taskon import NaiveTaskProcessor

# import MultiThreadTaskProcessor

def MakeSandwitch(bread, onion, grill_duration):
  print("Cutting " + onion)
  print("Grilling " + bread + " for " + str(grill_duration) + " minutes")
  return onion + "-Sandwitch"

def MakeBread(flour):
  print("Processing " + flour)
  return "Bread"

def BuyOnion():
  return "Onion"

t1 = SimpleTask(name = "make_sandwitch",
                action = MakeSandwitch,
                args = (TaskResult("make_bread"), TaskResult("buy_onion"), 4))

t2 = SimpleTask(name = "make_bread", action = MakeBread, args=("flour",))

t3 = SimpleTask(name = "buy_onion", action = BuyOnion)

# task_processor = MultiThreadTaskProcessor(max_thread=10)
task_processor = NaiveTaskProcessor()
task_runner = TaskRunner(tasks = [t1, t2, t3],
                                target_tasks = [t1],
                                task_processor = task_processor)
task_runner.run()

assert task_runner.getTask("make_sandwitch").getStatus() == TaskStatus.SUCCESS
assert task_runner.getTask("make_sandwitch").getResult() == "Onion-Sandwitch"
