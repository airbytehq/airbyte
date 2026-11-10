from pathlib import Path

import tomllib
from packaging.specifiers import SpecifierSet


def test_pyproject_requires_python_3_11_or_newer():
    pyproject = tomllib.loads((Path(__file__).parent.parent / "pyproject.toml").read_text())
    python_spec = SpecifierSet(pyproject["tool"]["poetry"]["dependencies"]["python"])
    assert "3.10.12" not in python_spec
    assert "3.11.0" in python_spec
