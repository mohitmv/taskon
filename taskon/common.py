import enum

class TaskonError(Exception):
    """General TaskonError"""
    pass

class TaskonFatalError(Exception):
    """
    TaskonFatalError is non recoverable exception and it should not be catched
    """
    pass

def taskonAssert(condition, msg):
    if not condition:
        raise TaskonFatalError(msg)

class TaskResult:
    """Placeholder for task result."""
    def __init__(self, name):
        self.name = name

class TaskStatus(enum.IntEnum):
    SUCCESS = 1
    FAILURE = 2
    ABORTED = 3
    NOT_EXECUTED = 4


class Object(dict):
    """
    Object extends the inbuilt dictionary and exposes the keys as class members.
    p = Object({"key1": 11, "key2": 22})
    key1 of p can be accessed by p.key1 as well as p["key1"].
    """
    def __init__(self, *initial_value, **kwargs):
        self.__dict__ = self
        dict.__init__(self, *initial_value, **kwargs)