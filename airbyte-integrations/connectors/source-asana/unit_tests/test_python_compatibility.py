# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import re
from pathlib import Path

from packaging.specifiers import SpecifierSet


def test_pyproject_python_constraint_allows_base_image_python():
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    pyproject_text = pyproject_path.read_text()

    try:
        import tomllib
    except ModuleNotFoundError:
        dependency_section = re.search(r"(?ms)^\[tool\.poetry\.dependencies\]\s*\n(.*?)(?=^\[|\Z)", pyproject_text)
        assert dependency_section is not None
        python_constraint = re.search(
            r'(?m)^\s*python\s*=\s*"([^"]+)"\s*$',
            dependency_section.group(1),
        )
        assert python_constraint is not None
        constraint = python_constraint.group(1)
    else:
        constraint = tomllib.loads(pyproject_text)["tool"]["poetry"]["dependencies"]["python"]

    specifiers = []
    for part in constraint.split(","):
        part = part.strip()
        if part.startswith("^"):
            version = part[1:]
            major = int(version.split(".")[0])
            specifiers.extend((f">={version}", f"<{major + 1}.0"))
        else:
            specifiers.append(part)

    python_specifier = SpecifierSet(",".join(specifiers))
    assert python_specifier.contains("3.13.14")
    assert python_specifier.contains("3.10.0")
