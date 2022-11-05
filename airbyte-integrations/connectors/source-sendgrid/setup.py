#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os

from setuptools import find_packages, setup

AIRBYTE_ROOT = os.environ.get("AIRBYTE_ROOT") or "/".join(os.getcwd().split("/")[:-3])
PATH_TO_CDK = f"{AIRBYTE_ROOT}/airbyte-cdk/python#egg=airbyte_cdk"

MAIN_REQUIREMENTS = [
    f"airbyte-cdk @ file://{PATH_TO_CDK}#egg=airbyte_cdk",
    "backoff",
    "requests",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "source-acceptance-test",
    "requests-mock",
]

setup(
    name="source_sendgrid",
    description="Source implementation for Sendgrid.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
