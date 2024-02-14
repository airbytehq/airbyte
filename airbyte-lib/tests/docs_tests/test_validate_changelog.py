# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import tomli


def test_validate_changelog():
    """
    Publishing a version involves bumping the version in pyproject.toml and adding a changelog entry.
    This test ensures that the changelog entry is present.
    """

    # get the version from pyproject.toml
    with open("pyproject.toml") as f:
        contents = tomli.loads(f.read())
        version = contents["tool"]["poetry"]["version"]

    # get the changelog
    with open("README.md") as f:
        readme = f.read()
    changelog = readme.split("## Changelog")[-1]

    # check that the changelog contains the version
    assert version in changelog, f"Version {version} is missing from the changelog in README.md. Please add it."
