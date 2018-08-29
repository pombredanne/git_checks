# coding=utf-8
"""
Are things in place for successful upload to pypi
- twine, setup.py etc.
"""

import os


class PypiBuildChecks(object):
    def __init__(self):
        self.problems = []

    def find_problems(self):
        if not os.path.isfile("setup.py"):
            self.problems.append("Need setup.py!")
        if not os.path.isfile("MANEFEST.in"):
            self.problems.append("Need MANEFEST.in! (if you have non .py dependencies)")
        if not os.path.isfile("README.rst"):
            self.problems.append("Need README.rst!")
            if os.path.isfile("README.MD"):
                self.problems.append(
                    "Have README.MD, maybe you need to convert using pandoc!"
                )
        for problem in self.problems:
            print(problem)
