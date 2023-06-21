#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from pathlib import Path

from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["requests", "click~=8.1.3", "pyyaml"]


def local_pkg(name: str) -> str:
    """Returns a path to a local package."""
    return f"{name} @ file://{Path.cwd().parent / name}"


# These internal packages are not yet published to a Pypi repository.
LOCAL_REQUIREMENTS = [local_pkg("ci_common_utils")]

TEST_REQUIREMENTS = ["requests-mock", "pytest"]

setup(
    version="1.1.0",
    name="ci_credentials",
    description="CLI tooling to read and manage GSM secrets",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS + LOCAL_REQUIREMENTS,
    python_requires=">=3.9",
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
    entry_points={
        "console_scripts": [
            "ci_credentials = ci_credentials.main:ci_credentials",
        ],
    },
)
