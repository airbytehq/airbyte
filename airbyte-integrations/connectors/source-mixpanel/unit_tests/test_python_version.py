#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import re
from pathlib import Path

import tomllib


PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def test_minimum_python_version_is_3_11() -> None:
    constraint = tomllib.loads(PYPROJECT.read_text())["tool"]["poetry"]["dependencies"]["python"]
    match = re.match(r"^[\^>=~]*\s*(\d+)\.(\d+)", constraint)
    assert match, constraint
    assert (int(match.group(1)), int(match.group(2))) >= (3, 11), constraint
