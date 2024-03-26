#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from pathlib import Path

from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "click"]


def local_pkg(name: str) -> str:
    """Returns a path to a local package."""
    return f"{name} @ file://{Path.cwd().parent / name}"


# These internal packages are not yet published to a Pypi repository.
LOCAL_REQUIREMENTS = [local_pkg("ci_credentials")]

TEST_REQUIREMENTS = ["pytest", "pytest-mock", "pyfakefs"]

setup(
    version="0.0.1",
    name="source_update",
    description="CLI tooling to update a source using Connector Builder output",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS + LOCAL_REQUIREMENTS,
    python_requires=">=3.9",
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
