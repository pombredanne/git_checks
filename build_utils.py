# coding=utf-8
"""
Things I wish pynt_contrib had.
"""
import functools
import os
import socket
import subprocess

from checksumdir import dirhash
from semantic_version import Version

PROJECT_NAME = "git_checks"
SRC = '.'
# for multitargeting
PYTHON = "python"
IS_DJANGO = False
IS_TRAVIS = 'TRAVIS' in os.environ
if IS_TRAVIS:
    PIPENV = ""
else:
    PIPENV = "pipenv run"
GEM_FURY = ""

CURRENT_HASH = None

MAC_LIBS = ":"


def check_is_aws():
    """

    :rtype: bool
    """
    name = socket.getfqdn()
    return "ip-" in name and ".ec2.internal" in name


# bash to find what has change recently
# find src/ -type f -print0 | xargs -0 stat -f "%m %N" | sort -rn | head -10 | cut -f2- -d" "
class BuildState(object):
    def __init__(self, what, where):
        self.what = what
        self.where = where
        if not os.path.exists(".build_state"):
            os.makedirs(".build_state")
        self.state_file_name = ".build_state/last_change_{0}.txt".format(what)

    def oh_never_mind(self):
        """
        If a task fails, we don't care if it didn't change since last, re-run,
        :return:
        """
        os.remove(self.state_file_name)

    def has_source_code_tree_changed(self):
        """
        If a task succeeds & is re-run and didn't change, we might not
        want to re-run it if it depends *only* on source code
        :return:
        """
        global CURRENT_HASH
        directory = self.where

        # if CURRENT_HASH is None:
        # print("hashing " + directory)
        # print(os.listdir(directory))
        CURRENT_HASH = dirhash(directory, 'md5', ignore_hidden=True,
                               # changing these exclusions can cause dirhas to skip EVERYTHING
                               #excluded_files=[".coverage", "lint.txt"],
                               excluded_extensions=[".pyc"]
                               )

        print("Searching " + self.state_file_name)
        if os.path.isfile(self.state_file_name):
            with open(self.state_file_name, "r+") as file:
                last_hash = file.read()
                if last_hash != CURRENT_HASH:
                    file.seek(0)
                    file.write(CURRENT_HASH)
                    file.truncate()
                    return True
                else:
                    return False

        # no previous file, by definition not the same.
        with open(self.state_file_name, "w") as file:
            file.write(CURRENT_HASH)
            return True


def oh_never_mind(what):
    state = BuildState(what, PROJECT_NAME)
    state.oh_never_mind()


def has_source_code_tree_changed(task_name, expect_file=None):
    if expect_file:
        if os.path.isdir(expect_file) and not os.listdir(expect_file):
            os.path.dirname(expect_file)
            # output folder empty
            return True
        if not os.path.isfile(expect_file):
            # output file gone
            return True
    state = BuildState(task_name, os.path.join(SRC, PROJECT_NAME))
    return state.has_source_code_tree_changed()


def skip_if_no_change(name, expect_files=None):
    # https://stackoverflow.com/questions/5929107/decorators-with-parameters
    def real_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not has_source_code_tree_changed(name, expect_files):
                print("Nothing changed, won't re-" + name)
                return
            try:
                return func(*args, **kwargs)
            except:
                oh_never_mind(name)
                raise

        return wrapper

    return real_decorator


def execute_with_environment(command, env):
    # Python 2 code! Python 3 uses context managers.
    shell_process = subprocess.Popen(command.strip().replace("  ", " ").split(" "), env=env)
    value = shell_process.communicate()  # wait
    if shell_process.returncode != 0:
        print("Didn't get a zero return code, got : {0}".format(shell_process.returncode))
        exit(-1)
        # raise TypeError("Didn't get a zero return code, got : {0}".format(shell_process.returncode))
    return value


def execute_get_text(command):  # type: (str) ->str
    """
    Execute shell command and return stdout txt
    :param command:
    :return:
    """
    try:
        _ = subprocess.run
        try:
            completed = subprocess.run(
                command,
                check=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as cpe:
            raise
        else:
            return completed.stdout.decode('utf-8') + completed.stderr.decode("utf-8")
    except AttributeError:
        try:
            p = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
            out, err = p.communicate()
        except subprocess.CalledProcessError as cpe:
            raise
        else:
            return str(out) + str(err)






def get_packages():
    packages = []
    cp = subprocess.run(("fury list --as={0}".format(GEM_FURY).split(" ")),
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        shell=False, check=True)
    package_text = cp.stdout.split("\n")
    found = False
    for line in package_text:
        if "(" in line and ")" in line:
            if PROJECT_NAME in line:
                found = True
            packages.append(line)
    return packages, found


def get_versions():
    versions = []
    cp = subprocess.run(("fury versions {0} --as={0}".format(GEM_FURY).format(PROJECT_NAME).split(" ")),
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        shell=False, check=True)
    package_text = cp.stdout.decode().split("\n")
    found = False
    for line in package_text:
        if "." in line:
            try:
                version = Version(line)
                versions.append(version)
            except ValueError:
                pass
    print(versions)
    return versions
