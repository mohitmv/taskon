#! /usr/bin/env python3

import unittest, sys

from taskon.tests.basic_test import TaskonBasicTest
from taskon.tests.basic_test import TaskonBasicErrorTest
from taskon.tests.basic_test import ContinueOnFailureTest
from taskon.tests.basic_test import BashCommandTest

from taskon.tests.error_validation import ErrorValidationTest

from taskon.tests.utils_test import TaskonUtilsTest

from taskon.tests.task_processor_test import FiniteThreadTaskProcessorTest

unittest.main()
