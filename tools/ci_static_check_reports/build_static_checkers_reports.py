#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import os
import sys

from invoke import Context
from tasks import CONFIG_FILE, TASK_COMMANDS, TOOLS_VERSIONS, _run_task


def update_task_commands_to_generate_reports(module_path: str) -> None:
    # TODO: update tasks runner after its deployed (https://github.com/airbytehq/airbyte/pull/8873) and refactor this codeblock
    for task, commands in TASK_COMMANDS.items():
        if task == "black":
            commands[-1] = (
                f"XDG_CACHE_HOME={os.devnull} black -v {{check_option}} "
                f"--diff {{source_path}}/. > static_checker_reports/{module_path}/black.txt"
            )
        elif task == "coverage":
            commands[-1] = f"{commands[-1]} > static_checker_reports/{module_path}/coverage.txt"
        elif task == "flake":
            commands[-1] = f"{commands[-1]} > static_checker_reports/{module_path}/flake.txt"
        elif task == "isort":
            commands[-1] = f"pflake8 -v --diff {{source_path}} > static_checker_reports/{module_path}/isort.txt"
        elif task == "mypy":
            commands.insert(-1, f"pip install lxml~={TOOLS_VERSIONS['lxml']}")
            commands[-1] = f"mypy {{source_path}} --config-file={CONFIG_FILE} --cobertura-xml-report=static_checker_reports/{module_path}"
        elif task == "test":
            commands[-1] = (
                f"pytest -v --cov={{source_path}} --cov-report xml:static_checker_reports/{module_path}/pytest.xml "
                f"{{source_path}}/unit_tests"
            )


def build_static_checkers_reports(modules: list) -> None:
    ctx = Context()
    for module_path in modules:
        update_task_commands_to_generate_reports(module_path)
        for checker in TASK_COMMANDS.keys():
            _run_task(ctx, module_path, checker, multi_envs=False, check_option="")


if __name__ == "__main__":
    print("Changed modules: ", sys.argv[1:])
    build_static_checkers_reports(sys.argv[1:])
