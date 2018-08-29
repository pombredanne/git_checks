# coding=utf-8
"""
Git Checks.

Usage:
  git_checks
  git_checks -h | --help
  git_checks --version

Options:
  --version            Show version of jiggle_version, not your apps.
  -h --help            Show this screen.

"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import configparser
import logging
import logging.config
from typing import List, Optional, Dict, Any

from docopt import docopt

from git_checks._version import __version__
from git_checks.files_checker import FilesChecker
from git_checks.pynt_checks import PyntBuildChecks
from git_checks.pypi_checks import PypiBuildChecks

logger = logging.getLogger(__name__)

# contrive usage so formatter doesn't remove the import
_ = List, Optional, Dict, Any


def process_docopts(test=None):  # type: (Optional[Dict[str,Any]])->None
    """
    Just process the command line options and commands
    :return:
    """
    if test:
        arguments = test
    else:
        arguments = docopt(__doc__, version="Jiggle Version {0}".format(__version__))


"""

TODO:

Check that checkin/push hooks are in place, install if not. Driven by .ini file.

Check that .gitignore contains certain things. Driven by .ini file
- no .zip files

Check that source tree has no .zip files or other compressed files
- ref https://en.wikipedia.org/wiki/List_of_archive_formats

 git check-ignore git_checks/foo.zip -- reports if it is already ignored.

"""
import os


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("../test/.git_checks.ini")
    checker = FilesChecker("..")
    checker.search_all()
    pynt_checker = PyntBuildChecks()

    pypi_checks = PypiBuildChecks()