import unittest

from taskon.common import taskonAssert
from taskon.common import TaskonFatalError
from taskon.tests.test_utils import writeFile, readFile


class TaskonUtilsTest(unittest.TestCase):
    def test_taskonAssert(self):
        taskonAssert(True, "No Error")
        with self.assertRaises(TaskonFatalError) as context:
            taskonAssert(False, "Some Error")
        self.assertEqual('Some Error', str(context.exception))

    def test_writeFile(self):
        file = "/tmp/taskon_null_test_writeFile"
        writeFile(file, "XyZ")
        self.assertEqual(readFile(file), "XyZ")
