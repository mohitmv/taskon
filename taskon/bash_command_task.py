import os
from taskon.common import TaskonError
from taskon.abortable_task import AbortableTask

class BashCommandTask(AbortableTask):
    def __init__(self, name, bash_command, args=None, kwargs=None, result=None):
        AbortableTask.__init__(self, name, args, kwargs, result)
        self.bash_command = bash_command

    def getCommand(self):
        return self.bash_command

    def run(self, *args, **params):
        result = os.system(self.bash_command)
        if (result >> 8) != 0:
            raise TaskonError(
                "Failed to execute command: '%s'\nExit code: %s",
                (self.bash_command, (result >> 8)))
