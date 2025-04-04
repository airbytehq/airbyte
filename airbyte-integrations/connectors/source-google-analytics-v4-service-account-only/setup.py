#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

from setuptools import find_packages, setup


def local_dependency(name: str) -> str:
    """Returns a path to a local package."""
    return f"{name} @ file://{Path.cwd().parent / name}"


MAIN_REQUIREMENTS = ["airbyte-cdk", "PyJWT", "cryptography", "requests", local_dependency("source-google-analytics-v4")]

TEST_REQUIREMENTS = [
    "pytest~=8.0",
    "requests-mock",
    "pytest-mock",
    "freezegun",
]

setup(
    name="source_google_analytics_v4_service_account_only",
    description="Source implementation for Google Analytics V4.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={
        "": [
            # Include yaml files in the package (if any)
            "*.yml",
            "*.yaml",
            # Include all json files in the package, up to 4 levels deep
            "*.json",
            "*/*.json",
            "*/*/*.json",
            "*/*/*/*.json",
            "*/*/*/*/*.json",
        ]
    },
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
