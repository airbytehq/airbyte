#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import os
import shutil
import tempfile
from glob import glob
from multiprocessing import Pool
from typing import Any, Dict, Iterable, List, Optional, Set

import virtualenv
from invoke import Context, Exit, task

CONNECTORS_DIR: str = os.path.abspath(os.path.curdir)

ROOT_DIR = os.path.dirname(os.path.dirname(CONNECTORS_DIR))
CONFIG_FILE: str = os.path.join(ROOT_DIR, "pyproject.toml")

# TODO: Get it from a single place with `pre-commit` (or make pre-commit to use these tasks)
TOOLS_VERSIONS: Dict[str, str] = {
    "black": "21.12b0",
    "colorama": "0.4.4",
    "coverage": "6.2",
    "flake": "0.0.1a2",
    "flake_junit": "2.1",
    "isort": "5.10.1",
    "mccabe": "0.6.1",
    "mypy": "0.910",
    "lxml": "4.7",
}

TASK_COMMANDS: Dict[str, List[str]] = {
    "black": [
        f"pip install black~={TOOLS_VERSIONS['black']}",
        f"XDG_CACHE_HOME={os.devnull} black -v {{check_option}} {{source_path}}/.",
    ],
    "coverage": [
        "pip install .",
        f"pip install coverage[toml]~={TOOLS_VERSIONS['coverage']}",
        f"coverage report --rcfile={CONFIG_FILE}",
    ],
    "flake": [
        f"pip install mccabe~={TOOLS_VERSIONS['mccabe']}",
        f"pip install pyproject-flake8~={TOOLS_VERSIONS['flake']}",
        "pflake8 -v {source_path}",
    ],
    "isort": [
        f"pip install colorama~={TOOLS_VERSIONS['colorama']}",
        f"pip install isort~={TOOLS_VERSIONS['isort']}",
        "isort -v {check_option} {source_path}/.",
    ],
    "mypy": [
        "pip install .",
        f"pip install mypy~={TOOLS_VERSIONS['mypy']}",
        "mypy --install-types --non-interactive ",
        f"mypy {{source_path}} --config-file={CONFIG_FILE}",
    ],
    "test": [
        f"cp -rf {os.path.join(CONNECTORS_DIR, os.pardir, 'bases', 'source-acceptance-test')} {{venv}}/",
        "pip install build",
        f"python -m build {os.path.join('{venv}', 'source-acceptance-test')}",
        f"pip install {os.path.join('{venv}', 'source-acceptance-test', 'dist', 'source_acceptance_test-*.whl')}",
        "pip install .",
        "pip install .[tests]",
        "pip install pytest-cov",
        "pytest -v --cov={source_path} --cov-report xml unit_tests",
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


def _run_single_connector_task(args: Iterable) -> int:
    """
    Wrapper for unpack task arguments.
    """
    return _run_task(*args)


def _run_task(
    ctx: Context,
    connector_string: str,
    task_name: str,
    multi_envs: bool = True,
    module_path: Optional[str] = None,
    task_commands: Dict = TASK_COMMANDS,
    **kwargs: Any,
) -> int:
    """
    Run task in its own environment.
    """
    cur_dir = os.getcwd()
    if multi_envs:
        if module_path:
            os.chdir(module_path)
            source_path = connector_string
        else:
            os.chdir(os.path.join(CONNECTORS_DIR, f"source-{connector_string}"))
            source_path = f"source_{connector_string.replace('-', '_')}"

    else:
        source_path = connector_string

    venv_name = tempfile.mkdtemp(dir=os.curdir)
    virtualenv.cli_run([venv_name])
    activator = os.path.join(os.path.abspath(venv_name), "bin", "activate")

    commands = []

    commands.extend([cmd.format(source_path=source_path, venv=venv_name, **kwargs) for cmd in task_commands[task_name]])

    exit_code: int = 0

    try:
        with ctx.prefix(f"source {activator}"):
            for command in commands:
                result = ctx.run(command, echo=True, warn=True)
                if result.return_code:
                    exit_code = 1
                    break
    finally:
        shutil.rmtree(venv_name, ignore_errors=True)

    if module_path:
        os.chdir(cur_dir)

    return exit_code


def apply_task_for_connectors(ctx: Context, connectors_names: str, task_name: str, multi_envs: bool = False, **kwargs: Any) -> None:
    """
    Run task commands for every connector or for once for a set of connectors, depending on task needs (`multi_envs` param).
    If `multi_envs == True` task for every connector runs in its own subprocess.
    """
    # TODO: Separate outputs to avoid a mess.

    connectors = connectors_names.split(",") if connectors_names else CONNECTORS_NAMES
    connectors = set(connectors) & CONNECTORS_NAMES

    exit_code: int = 0

    if multi_envs:
        print(f"Running {task_name} for the following connectors: {connectors}")

        task_args = [(ctx, connector, task_name) for connector in connectors]
        with Pool() as pool:
            for result in pool.imap_unordered(_run_single_connector_task, task_args):
                if result:
                    exit_code = 1

    else:
        source_path = " ".join([f"{os.path.join(CONNECTORS_DIR, f'source-{connector}')}" for connector in connectors])
        exit_code = _run_task(ctx, source_path, task_name, multi_envs=False, **kwargs)

    raise Exit(code=exit_code)


###########################################################################################################################################
# TASKS
###########################################################################################################################################

_arg_help_connectors = (
    "Comma-separated connectors' names without 'source-' prefix (ex.: -c github,google-ads,s3). "
    "The default is a list of all found connectors excluding the ones with `-singer` suffix."
)


@task(help={"connectors": _arg_help_connectors})
def all_checks(ctx, connectors=None):  # type: ignore[no-untyped-def]
    """
    Run following checks one by one with default parameters: black, flake, isort, mypy, test, coverage.
    Zero exit code indicates about successful passing of all checks.
    Terminate on the first non-zero exit code.
    """
    tasks = (
        black,
        flake,
        isort,
        mypy,
        coverage,
    )
    for task_ in tasks:
        try:
            task_(ctx, connectors=connectors)
        except Exit as e:
            if e.code:
                raise


@task(help={"connectors": _arg_help_connectors, "write": "Write changes into the files (runs 'black' without '--check' option)"})
def black(ctx, connectors=None, write=False):  # type: ignore[no-untyped-def]
    """
    Run 'black' checks for one or more given connector(s) code.
    Zero exit code indicates about successful passing of all checks.
    """
    check_option: str = "" if write else " --check"
    apply_task_for_connectors(ctx, connectors, "black", check_option=check_option)


@task(help={"connectors": _arg_help_connectors})
def flake(ctx, connectors=None):  # type: ignore[no-untyped-def]
    """
    Run 'flake8' checks for one or more given connector(s) code.
    Zero exit code indicates about successful passing of all checks.
    """
    apply_task_for_connectors(ctx, connectors, "flake")


@task(help={"connectors": _arg_help_connectors, "write": "Write changes into the files (runs 'isort' without '--check' option)"})
def isort(ctx, connectors=None, write=False):  # type: ignore[no-untyped-def]
    """
    Run 'isort' checks for one or more given connector(s) code.
    Zero exit code indicates about successful passing of all checks.
    """
    check_option: str = "" if write else " --check"
    apply_task_for_connectors(ctx, connectors, "isort", check_option=check_option)


@task(help={"connectors": _arg_help_connectors})
def mypy(ctx, connectors=None):  # type: ignore[no-untyped-def]
    """
    Run MyPy checks for one or more given connector(s) code.
    A virtual environment is being created for every one.
    Zero exit code indicates about successful passing of all checks.
    """
    apply_task_for_connectors(ctx, connectors, "mypy", multi_envs=True)


@task(help={"connectors": _arg_help_connectors})
def test(ctx, connectors=None):  # type: ignore[no-untyped-def]
    """
    Run unittests for one or more given connector(s).
    A virtual environment is being created for every one.
    Zero exit code indicates about successful passing of all tests.
    """
    apply_task_for_connectors(ctx, connectors, "test", multi_envs=True)


@task(help={"connectors": _arg_help_connectors})
def coverage(ctx, connectors=None):  # type: ignore[no-untyped-def]
    """
    Check test coverage of code for one or more given connector(s).
    A virtual environment is being created for every one.
    "test" command is being run before this one.
    Zero exit code indicates about enough coverage level.
    """
    try:
        test(ctx, connectors=connectors)
    except Exit as e:
        if e.code:
            raise
        apply_task_for_connectors(ctx, connectors, "coverage", multi_envs=True)
