#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import os.path
from glob import glob
from typing import List

import nox

CONNECTORS_DIR: str = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    ),
    "connectors"
)

MYPY_VERSION: str = "0.910"

CONFIG_FILE: str = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
        )
    ),
    "pyproject.toml"
)


def get_connectors_names() -> List[str]:
    cur_dir = os.path.abspath(os.curdir)
    os.chdir(CONNECTORS_DIR)
    names = []
    for name in glob("source-*"):
        if os.path.exists(os.path.join(name, "setup.py")):
            names.append(name.split("source-", 1)[1])
    os.chdir(cur_dir)
    return names


connectors_names = get_connectors_names()


@nox.session
@nox.parametrize("connector_name", connectors_names, ids=connectors_names)
def mypy(session: nox.Session, connector_name: str):
    source_dir = f"source_{connector_name.replace('-', '_')}"
    cur_dir = os.path.abspath(os.curdir)
    os.chdir(os.path.join(CONNECTORS_DIR, f"source-{connector_name}"))

    # MyPy
    session.install(f"mypy~={MYPY_VERSION}")
    session.run("mypy", source_dir, f"--config-file={CONFIG_FILE}")
    os.chdir(cur_dir)


@nox.session
@nox.parametrize("connector_name", connectors_names, ids=connectors_names)
def tests(session: nox.Session, connector_name: str):
    source_dir = f"source_{connector_name.replace('-', '_')}"
    cur_dir = os.path.abspath(os.curdir)
    os.chdir(os.path.join(CONNECTORS_DIR, f"source-{connector_name}"))

    # Requirements
    session.install("-r", "requirements.txt", success_codes=[0, 1])

    # Unit tests
    session.install(".[tests]")
    session.install("pytest-cov", "pytest-xdist[psutil]")
    session.run("pytest", f"--cov={source_dir}", "-n", "auto", "unit_tests")
