import os
import shutil
import sys
import tempfile
from glob import glob
from itertools import zip_longest
from multiprocessing import Pool
from subprocess import PIPE, Popen
from typing import Dict, List, Sequence, Set, Tuple

import invoke
from invoke import task

ROOT_PROJECT_DIR: str = os.path.abspath(os.path.curdir)

CONFIG_FILE: str = os.path.join(ROOT_PROJECT_DIR, "pyproject.toml")

CONNECTORS_DIR: str = os.path.join(ROOT_PROJECT_DIR, "airbyte-integrations", "connectors")

# TODO: Get it from a single place with `pre-commit` (or make pre-commit use these tasks)
TOOLS_VERSIONS: Dict[str, str] = {
    "black": "21.12b0",
    "colorama": "0.4.4",
    "flake": "0.0.1a2",
    "isort": "5.10.1",
    "mccabe": "0.6.1",
    "mypy": "0.910",
}


TASK_COMMANDS: Dict[str, List[str]] = {
    "black": [
        f"pip install black~={TOOLS_VERSIONS['black']}",
        f"black -v {{check_option}} {{source_dir}}/.",
    ],
    "flake": [
        f"pip install mccabe~={TOOLS_VERSIONS['mccabe']}",
        f"pip install pyproject-flake8~={TOOLS_VERSIONS['flake']}",
        f"pflake8 -v {{source_dir}}",
    ],
    "isort": [
        f"pip install colorama~={TOOLS_VERSIONS['colorama']}",
        f"pip install isort~={TOOLS_VERSIONS['isort']}",
        f"isort -v {{check_option}} {{source_dir}}/.",
    ],
    "mypy": [
        f"pip install mypy~={TOOLS_VERSIONS['mypy']}",
        f"mypy {{source_dir}} --config-file={CONFIG_FILE}",
    ],
    "test": [
        "pip install .[tests]",
        "pip install pytest-cov",
        "pytest -v --cov={source_dir} unit_tests",
    ],
}


###########################################################################################################################################
# HELPER FUNCTIONS
###########################################################################################################################################

def get_connectors_names() -> Set[str]:
    cur_dir = os.path.abspath(os.curdir)
    os.chdir(CONNECTORS_DIR)
    names = set()
    for name in glob("source-*"):
        if os.path.exists(os.path.join(name, "setup.py")):
            if not name.endswith("-singer"):  # There are some problems with those. The optimal way is to wait until it's replaced by CDK.
                names.add(name.split("source-", 1)[1].rstrip())

    os.chdir(cur_dir)
    return names


CONNECTORS_NAMES = get_connectors_names()


def _run_task(args: Sequence[str], multi_envs=True, **kwargs) -> Tuple[int, str, str]:
    # TODO: smartly separate for multi calls. `subprocess.run()` could be ok (and easier) for that case.
    connector_string, task_name = args
    if multi_envs:
        source_dir = f"source_{connector_string.replace('-', '_')}"
        os.chdir(os.path.join(CONNECTORS_DIR, f"source-{connector_string}"))
    else:
        source_dir = connector_string

    runner = Popen("bash", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    venv_name = tempfile.mkdtemp(dir=os.curdir)
    commands = [
        f"virtualenv {venv_name}",
        f"source {os.path.join(venv_name, 'bin', 'activate')}",
    ]
    if multi_envs:
        commands.extend([
            "pip install -r requirements.txt",
        ])

    commands.extend([cmd.format(source_dir=source_dir, **kwargs) for cmd in TASK_COMMANDS[task_name]])

    runner.stdin.writelines(f"{cmd}\n".encode() for cmd in commands)
    runner.stdin.flush()
    out, err = runner.communicate()
    shutil.rmtree(venv_name)
    return runner.returncode, out.decode(), err.decode()


def apply_task_for_connectors(connectors_names: str, task_name: str, multi_envs=False, **kwargs):
    connectors = connectors_names.split(",") if connectors_names else CONNECTORS_NAMES

    connectors = set(connectors) & CONNECTORS_NAMES

    exit_code: int = 0

    if multi_envs:
        with Pool() as pool:
            for result in pool.imap_unordered(_run_task, zip_longest(connectors, [], fillvalue=task_name)):
                print(result[1], file=sys.stdout)
                print()
                print(result[2], file=sys.stderr)
                print()

                if result[0]:
                    exit_code = 1
    else:
        source_dir = " ".join(
            [f"{os.path.join(CONNECTORS_DIR, f'source-{connector}')}" for connector in connectors]
        )
        result = _run_task([source_dir, task_name], multi_envs=False, **kwargs)
        print(result[1], file=sys.stdout)
        print()
        print(result[2], file=sys.stderr)
        exit_code = result[0]

    raise invoke.Exit(code=exit_code)


###########################################################################################################################################
# TASKS
###########################################################################################################################################

_arg_help_connectors = (
    "Comma-separated connectors' names without 'source-' prefix (ex.: -c github,google-ads,s3). "
    "The default is a list of all found connectors."
)


@task(help={"connectors": _arg_help_connectors, "write": "Write changes into the files (runs 'black' without '--check' option)"})
def black(ctx, connectors=None, write=False):  # type: ignore[no-untyped-def]
    """
    Run 'black' checks for one or more given connector(s) code.
    Zero exit code indicates about successful passing of all checks.
    """
    check_option: str = "" if write else " --check"
    apply_task_for_connectors(connectors, "black", check_option=check_option)


@task(help={"connectors": _arg_help_connectors})
def flake(ctx, connectors=None):  # type: ignore[no-untyped-def]
    """
    Run 'flake8' checks for one or more given connector(s) code.
    Zero exit code indicates about successful passing of all checks.
    """
    apply_task_for_connectors(connectors, "flake")


@task(help={"connectors": _arg_help_connectors, "write": "Write changes into the files (runs 'black' without '--check' option)"})
def isort(ctx, connectors=None, write=False):  # type: ignore[no-untyped-def]
    """
    Run 'isort' checks for one or more given connector(s) code.
    Zero exit code indicates about successful passing of all checks.
    """
    check_option: str = "" if write else " --check"
    apply_task_for_connectors(connectors, "isort", check_option=check_option)


@task(help={"connectors": _arg_help_connectors})
def mypy(ctx, connectors=None):  # type: ignore[no-untyped-def]
    """
    Run MyPy checks for one or more given connector(s) code.
    A virtual environment is being created for every one.
    Zero exit code indicates about successful passing of all checks.
    """
    apply_task_for_connectors(connectors, "mypy", multi_envs=True)


@task(help={"connectors": _arg_help_connectors})
def test(ctx, connectors=None):  # type: ignore[no-untyped-def]
    """
    Run unittests for one or more given connector(s).
    A virtual environment is being created for every one.
    Zero exit code indicates about successful passing of all tests.
    """
    apply_task_for_connectors(connectors, "test", multi_envs=True)
