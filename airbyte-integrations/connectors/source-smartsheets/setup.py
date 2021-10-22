#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "smartsheet-python-sdk"
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "source-acceptance-test",
]
setup(
    name="source_smartsheets",
    description="Source implementation for Smartsheets.",
    author="Nate Nowack",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
