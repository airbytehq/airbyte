import os
import shutil
import time
from glob import glob
from itertools import zip_longest
from multiprocessing import Pool
from subprocess import Popen, PIPE
from typing import List, Tuple, Set, Dict
from uuid import uuid4

from invoke import task


ROOT_PROJECT_DIR: str = os.path.abspath(os.path.curdir)

CONFIG_FILE: str = os.path.join(ROOT_PROJECT_DIR, "pyproject.toml")

CONNECTORS_DIR: str = os.path.join(
    ROOT_PROJECT_DIR, "airbyte-integrations", "connectors"
)

MYPY_VERSION: str = "0.910"


TASK_COMMANDS: Dict[str, List[str]] = {
    "mypy": [
        f"pip install mypy~={MYPY_VERSION}",
        f"mypy {{source_dir}} --config-file={CONFIG_FILE}",
    ],
    "test": [
        "pip install pytest-cov",
        "pytest --cov={source_dir} unit_tests",
    ],
}


def get_connectors_names() -> Set[str]:
    cur_dir = os.path.abspath(os.curdir)
    os.chdir(CONNECTORS_DIR)
    names = set()
    for name in glob("source-*"):
        if os.path.exists(os.path.join(name, "setup.py")):
            names.add(name.split("source-", 1)[1].rstrip())
    os.chdir(cur_dir)
    return names


CONNECTORS_NAMES = get_connectors_names()


def run_task(args) -> Tuple[bool, str]:
    connector_name, task_name = args
    source_dir = f"source_{connector_name.replace('-', '_')}"
    os.chdir(os.path.join(CONNECTORS_DIR, f"source-{connector_name}"))

    runner = Popen("bash", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    venv_name = str(uuid4())
    commands = [
        f"virtualenv {venv_name}",
        f"source {os.path.join(venv_name, 'bin', 'activate')}",
        "pip install -r requirements.txt",
        "pip install .[tests]",
    ]
    commands.extend([cmd.format(source_dir=source_dir) for cmd in TASK_COMMANDS[task_name]])

    runner.stdin.writelines(f"{cmd}\n".encode() for cmd in commands)
    runner.stdin.flush()
    out, err = runner.communicate()
    shutil.rmtree(venv_name)
    return (False, err.decode()) if runner.returncode else (True, out.decode())


def apply_task_for_connectors(connectors_names: str, task_name: str):
    connectors = connectors_names.split(',') if connectors_names else CONNECTORS_NAMES

    connectors = set(connectors) & CONNECTORS_NAMES

    with Pool() as pool:
        for result in pool.imap_unordered(run_task, zip_longest(connectors, [], fillvalue=task_name)):  # TODO: handle differently depending on the first value
            print(result[1])


@task
def mypy(ctx, connectors=None):
    apply_task_for_connectors(connectors, "mypy")


@task
def test(ctx, connectors=None):
    apply_task_for_connectors(connectors, "test")
