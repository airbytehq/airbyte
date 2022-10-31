#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import os

from setuptools import find_packages, setup

AIRBYTE_ROOT = os.environ.get("AIRBYTE_ROOT") or "/".join(os.getcwd().split("/")[:-3])
PATH_TO_CDK = f"{AIRBYTE_ROOT}/airbyte-cdk/python#egg=airbyte_cdk"

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "pytest-mock~=3.6",
]

setup(
    name="source_greenhouse",
    description="Source implementation for Greenhouse.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=[f"airbyte-cdk @ file://{PATH_TO_CDK}#egg=airbyte_cdk", "dataclasses-jsonschema==2.15.1"],
    package_data={"": ["*.json", "*.yaml", "schemas/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
