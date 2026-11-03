#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
import re
import tomllib
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parent.parent
MINIMUM_PYTHON = (3, 11)


def _lower_bound(constraint: str) -> tuple:
    match = re.search(r"(?:\^|>=)\s*(\d+)\.(\d+)", constraint)
    assert match, f"No lower bound found in Python constraint {constraint!r}"
    return int(match.group(1)), int(match.group(2))


@pytest.mark.parametrize(
    "file_name,keys",
    [
        ("pyproject.toml", ("tool", "poetry", "dependencies", "python")),
        ("poetry.lock", ("metadata", "python-versions")),
    ],
)
def test_python_lower_bound_excludes_python_310(file_name, keys):
    data = tomllib.loads((PROJECT_ROOT / file_name).read_text())
    for key in keys:
        data = data[key]
    assert _lower_bound(data) >= MINIMUM_PYTHON
