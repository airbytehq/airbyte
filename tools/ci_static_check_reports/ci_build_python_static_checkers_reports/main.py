#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import argparse
import json
import os
import sys
from typing import Dict, List

from invoke import Context

sys.path.insert(0, "airbyte-integrations/connectors")
from tasks import CONFIG_FILE, TOOLS_VERSIONS, _run_task  # noqa

TASK_COMMANDS: Dict[str, List[str]] = {
    "black": [
        f"pip install black~={TOOLS_VERSIONS['black']}",
        f"XDG_CACHE_HOME={os.devnull} black -v {{check_option}} --diff {{source_path}}/. > {{reports_path}}/black.txt",
    ],
    "coverage": [
        "pip install .",
        f"pip install coverage[toml]~={TOOLS_VERSIONS['coverage']}",
        "coverage xml --rcfile={toml_config_file} -o {reports_path}/coverage.xml",
    ],
    "flake": [
        f"pip install mccabe~={TOOLS_VERSIONS['mccabe']}",
        f"pip install pyproject-flake8~={TOOLS_VERSIONS['flake']}",
        f"pip install flake8-junit-report~={TOOLS_VERSIONS['flake_junit']}",
        "pflake8 -v {source_path} --output-file={reports_path}/flake.txt --bug-report",
        "flake8_junit {reports_path}/flake.txt {reports_path}/flake.xml",
        "rm -f {reports_path}/flake.txt",
    ],
    "isort": [
        f"pip install colorama~={TOOLS_VERSIONS['colorama']}",
        f"pip install isort~={TOOLS_VERSIONS['isort']}",
        "isort -v {check_option} {source_path}/. > {reports_path}/isort.txt",
    ],
    "mypy": [
        "pip install .",
        f"pip install lxml~={TOOLS_VERSIONS['lxml']}",
        f"pip install mypy~={TOOLS_VERSIONS['mypy']}",
        "mypy {source_path} --config-file={toml_config_file} --cobertura-xml-report={reports_path}",
    ],
    "test": [
        "mkdir {venv}/source-acceptance-test",
        "cp -f $(git ls-tree -r HEAD --name-only {source_acceptance_test_path} | tr '\n' ' ') {venv}/source-acceptance-test",
        "pip install build",
        f"python -m build {os.path.join('{venv}', 'source-acceptance-test')}",
        f"pip install {os.path.join('{venv}', 'source-acceptance-test', 'dist', 'source_acceptance_test-*.whl')}",
        "[ -f requirements.txt ] && pip install -r requirements.txt 2> /dev/null",
        "pip install .",
        "pip install .[tests]",
        "pip install pytest-cov",
        "pytest -v --cov={source_path} --cov-report xml:{reports_path}/pytest.xml {source_path}/unit_tests",
    ],
}


def build_static_checkers_reports(modules: list, static_checker_reports_path: str) -> int:
    ctx = Context()
    toml_config_file = os.path.join(os.getcwd(), "pyproject.toml")

    for module_path in modules:
        reports_path = f"{os.getcwd()}/{static_checker_reports_path}/{module_path}"
        if not os.path.exists(reports_path):
            os.makedirs(reports_path)

        for checker in TASK_COMMANDS:
            _run_task(
                ctx,
                f"{os.getcwd()}/{module_path}",
                checker,
                module_path=module_path,
                multi_envs=True,
                check_option="",
                task_commands=TASK_COMMANDS,
                toml_config_file=toml_config_file,
                reports_path=reports_path,
                source_acceptance_test_path=os.path.join(os.getcwd(), "airbyte-integrations/bases/source-acceptance-test"),
            )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Working with Python Static Report Builder.")
    parser.add_argument("changed_modules", nargs="*")
    parser.add_argument("--static-checker-reports-path", help="SonarQube host", required=False, type=str, default="static_checker_reports")

    args = parser.parse_args()
    changed_python_module_paths = [
        module["dir"]
        for module in json.loads(args.changed_modules[0])
        if module["lang"] == "py" and os.path.exists(module["dir"]) and "setup.py" in os.listdir(module["dir"])
    ]
    print("Changed python modules: ", changed_python_module_paths)
    return build_static_checkers_reports(changed_python_module_paths, static_checker_reports_path=args.static_checker_reports_path)


if __name__ == "__main__":
    sys.exit(main())
