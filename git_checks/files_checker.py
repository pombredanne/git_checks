# coding=utf-8
"""
Check for oversized and zipped files.
"""

import os


class FilesChecker(object):
    def __init__(self, where):
        self.extensions = [".zip", ".gz", ".rar"]
        self.where = where

    def is_compressed(self, root, file):
        for extension in self.extensions:
            if file.endswith(extension):
                print(os.path.join(root, file))

    def search_all(self):
        for root, dirs, files in os.walk(self.where):
            for file in files:

                self.is_compressed(root, file)
                self.is_oversized(root, file)

    def is_ignored(self):
        raise NotImplementedError("run corresponding git")

    def is_oversized(self, root, file):
        full_name = os.path.join(root, file)
        statinfo = os.stat(full_name)
        if statinfo.st_size > 1000000000:
            print()
