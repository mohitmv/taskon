from taskon.common import TaskResult, TaskStatus

class AbstractTask:
    def __init__(self, name, args=None, kwargs=None, default_result=None):
        self.id = None
        self.name = name
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.default_result = default_result
        self.reset()

    def visitTaskResultPlaceholders(self, callback):
        """
        Visit over all the TaskResult placeholders used in the input of this
        task. input is the tuple (args, kwargs).
        """
        def visit(obj):
            if isinstance(obj, TaskResult):
                return callback(obj)
            elif isinstance(obj, list) or isinstance(obj, tuple):
                return type(obj)(visit(i) for i in obj)
            elif isinstance(obj, dict):
                return type(obj)((k, visit(v)) for k, v in obj.items())
            else:
                return obj
        return visit((self.args, self.kwargs))

    def setResult(self, result):
        self.result = result

    def getResult(self):
        return self.result

    def setError(self, error):
        self.error = error

    def getError(self):
        return self.error

    def getStatus(self):
        return self.status

    def reset(self):
        self.result = self.default_result
        self.status = TaskStatus.SKIPPED
        self.error = None


