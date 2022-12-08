#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

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
    install_requires=["airbyte-cdk~=0.1", "dataclasses-jsonschema==2.15.1"],
    package_data={"": ["*.json", "*.yaml", "schemas/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
