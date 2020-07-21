import os
from taskon.common import TaskonError
from taskon.abortable_task import AbortableTask
from taskon.utils import runCommand

class BashCommandTask(AbortableTask):
    def __init__(self, name, command, args=None, kwargs=None, result=None):
        AbortableTask.__init__(self, name, args, kwargs, result)
        self.command = command

    def run(self, *args, **kwargs):
        if callable(self.command):
            cmd = self.command(*args, **kwargs)
        else:
            cmd = self.command
        runCommand(cmd)
