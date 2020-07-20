from taskon.abstract_task import AbstractTask

"""
Contract of the AbortableTask.
Take a look at these implementation of AbortableTask for better understanding.
1. taskon.BashCommandTask
"""

class AbortableTask(AbstractTask):
    def __init__(self, name, args=None, kwargs=None, result=None):
        AbstractTask.__init__(self, name, args, kwargs, result)

    def abort(self):
        """
        An API to abort the running task. It should be implemented thread-safe.

        If this API is called even before task execution is started, task
        should not be execueted. A simple implementation could be to just
        maintain a boolean flag 'is_aborted' to skip the execution if task is
        aborted in advance.
        """
        pass
