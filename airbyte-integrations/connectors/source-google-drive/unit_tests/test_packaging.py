#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import tomllib


PYPROJECT_PATH = Path(__file__).parent.parent / "pyproject.toml"


def test_python_lower_bound_is_3_11():
    pyproject = tomllib.loads(PYPROJECT_PATH.read_text())
    python_constraint = pyproject["tool"]["poetry"]["dependencies"]["python"]
    assert python_constraint == "^3.11,<3.14"
