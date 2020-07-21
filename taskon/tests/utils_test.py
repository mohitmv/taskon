import unittest

from taskon.common import taskonAssert
from taskon.common import TaskonFatalError


class TaskonUtilsTest(unittest.TestCase):
    def test_taskonAssert(self):
        taskonAssert(True, "No Error")
        with self.assertRaises(TaskonFatalError) as context:
            taskonAssert(False, "Some Error")
        self.assertEqual('Some Error', str(context.exception))

