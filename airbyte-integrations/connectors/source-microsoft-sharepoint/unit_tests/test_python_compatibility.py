import importlib.metadata
from pathlib import Path

import tomllib
from packaging.specifiers import SpecifierSet


def test_python_constraint_allows_python_313():
    """Guard the Python 3.13 base image build (oncall#13758)."""
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    with pyproject_path.open("rb") as pyproject_file:
        pyproject = tomllib.load(pyproject_file)

    constraint = pyproject["tool"]["poetry"]["dependencies"]["python"]
    specifier = SpecifierSet(constraint)

    assert specifier.contains("3.13.0")
    assert specifier.contains("3.11.0")


def test_airbyte_cdk_major_version_supports_python_313():
    """Guard the Python 3.13 base image build (oncall#13758)."""
    cdk_version = importlib.metadata.version("airbyte-cdk")

    assert int(cdk_version.split(".", maxsplit=1)[0]) >= 7
