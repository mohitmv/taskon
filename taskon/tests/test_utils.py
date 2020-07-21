import os

from taskon.common import TaskonError

def readFile(fn, mode='r'):
    with open(fn, mode, encoding="utf8", errors='ignore') as fd:
        return fd.read()

def writeFile(fn, data, mode='w'):
    with open(fn, mode) as fd:
        fd.write(data)
