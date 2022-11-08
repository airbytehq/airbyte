#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os

from setuptools import find_packages, setup

PATH_TO_CDK = f"{os.getcwd()}/airbyte-cdk/python#egg=airbyte_cdk"

MAIN_REQUIREMENTS = [
    f"airbyte-cdk @ file://{PATH_TO_CDK}",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "pytest-mock~=3.6.1",
    "source-acceptance-test",
]

setup(
    name="source_sentry",
    description="Source implementation for Sentry.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
