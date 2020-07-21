import os

from taskon.common import TaskonError

def readFile(fn, mode='r'):
    with open(fn, mode, encoding="utf8", errors='ignore') as fd:
        return fd.read()

def writeFile(fn, data, mode='w'):
    with open(fn, mode) as fd:
        fd.write(data)

def runCommand(cmd):
    """Run a given bash command. Raise exception if command fails."""
    print("Running command: %s" % cmd)
    error_code = (os.system(cmd) >> 8)
    if error_code != 0:
        raise TaskonError(
            "Command '%s' failed with error_code %s" % (cmd, error_code))
