#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "pendulum~=2.1",
    "requests~=2.25",
]

TEST_REQUIREMENTS = ["pytest~=6.1", "pytest-mock~=3.6", "requests_mock~=1.8"]

setup(
    name="source_pipedrive",
    description="Source implementation for Pipedrive.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
