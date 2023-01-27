#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os

from setuptools import find_packages, setup

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "pytest-mock~=3.6",
]

CDK_VERSION = "airbyte-cdk~=0.1"

if os.getenv("LOCAL_CDK_DIR"):
    AIRBYTE_CDK = f"airbyte-cdk @ file://localhost/{os.getenv('LOCAL_CDK_DIR')}#egg=airbyte-cdk"
else:
    AIRBYTE_CDK = CDK_VERSION
setup(
    name="source_greenhouse",
    description="Source implementation for Greenhouse.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=[AIRBYTE_CDK, "dataclasses-jsonschema==2.15.1"],
    package_data={"": ["*.json", "*.yaml", "schemas/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
