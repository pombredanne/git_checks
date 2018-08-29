# coding=utf-8
"""
Checks related to doing a pynt build
"""
import os
import json


class PyntBuildChecks(object):
    def __init__(self):
        pass

    def build_themed(self):
        if not os.path.isfile("build.py"):
            print("No build file!")
        if not os.path.isdir(".build_state"):
            print(
                "No evidence having ever run pynt! (well one branch of it, not all of them write state files)"
            )
        if os.path.isfile(".build_state/last_build_date.txt"):
            with open(".build_state/last_build_date.txt", "r") as build_date_file:
                build_date_text = build_date_file.read()
