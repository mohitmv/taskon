from taskon.abstract_task import AbstractTask

class SimpleTask(AbstractTask):
    def __init__(self, name, action, args=None, kwargs=None, result=None):
        AbstractTask.__init__(self, name, args, kwargs, result)
        self.action = action

    def run(self, *args, **params):
        return self.action(*args, **params)
