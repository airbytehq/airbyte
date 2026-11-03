#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import re
import tomllib
from pathlib import Path


PYPROJECT_PATH = Path(__file__).resolve().parents[1] / "pyproject.toml"


def test_python_constraint_requires_at_least_3_11() -> None:
    constraint = tomllib.loads(PYPROJECT_PATH.read_text())["tool"]["poetry"]["dependencies"]["python"]
    lower_bound = re.match(r"\^(\d+)\.(\d+)", constraint)
    assert lower_bound, f"Unexpected python constraint format: {constraint}"
    assert tuple(map(int, lower_bound.groups())) >= (3, 11), f"Python 3.10 is no longer supported: {constraint}"
    assert "<3.14" in constraint, f"Python upper bound must stay <3.14: {constraint}"
