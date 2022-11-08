#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

<<<<<<< HEAD

from setuptools import find_packages, setup

=======
import os

from setuptools import find_packages, setup

PATH_TO_CDK = f"{os.getcwd()}/airbyte-cdk/python#egg=airbyte_cdk"

>>>>>>> alex/always_install_local_cdk
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
<<<<<<< HEAD
    install_requires=["airbyte-cdk~=0.1", "dataclasses-jsonschema==2.15.1"],
=======
    install_requires=[f"airbyte-cdk @ file://{PATH_TO_CDK}", "dataclasses-jsonschema==2.15.1"],
>>>>>>> alex/always_install_local_cdk
    package_data={"": ["*.json", "*.yaml", "schemas/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
