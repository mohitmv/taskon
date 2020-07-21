#! /usr/bin/env python3

import json

from taskon.utils import runCommand
from taskon.tests.test_utils import readFile

def printList(l):
    l = (l[:10] + ["..."]) if len(l) > 10 else l
    return "[" + (", ".join(str(x) for x in l)) + "]"

def main():
    runCommand("coverage erase")
    tests = ["unit_tests.py", "sandwitch_example.py", "benchmark_test.py"]
    coverage_run = "coverage run --source=. --omit=setup.py,coverage_test.py "\
                   "--append"
    for test in tests:
        runCommand(coverage_run + " " + test)
    runCommand("mkdir -p build")
    runCommand("coverage json -o build/coverage_report.json")
    coverage_report = json.loads(readFile("build/coverage_report.json"))
    coverage_failures = []
    files = coverage_report["files"]
    for file, info in files.items():
        if info["summary"]["missing_lines"] > 0:
            coverage_failures.append(file)
    coverage_failures.sort(
        key = lambda file: files[file]["summary"]["percent_covered"])
    runCommand("coverage html --directory build/coverage_html_report")
    if len(coverage_failures) > 0:
        print("-"*20)
        print("Missing coverage:")
        print("-"*5)
        for file in coverage_failures:
            summary = files[file]["summary"]
            missing = files[file]["missing_lines"]
            num_missing = summary["missing_lines"]
            num_lines = summary["num_statements"]
            missing_str = "%s/%s missing lines" % (num_missing, num_lines)
            line_info = file + ": " + missing_str
            line_info += " : Line no. " + printList(missing)
            print(line_info)
        print("-"*5)
        print("Open build/coverage_html_report/index.html in browser for "
              "detailed report")
        print("Coverage test failed")
        exit(1)
    else:
        print("Coverage test passed")

main()
