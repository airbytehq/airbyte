#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk>=0.42.0",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "pytest-mock~=3.6.1",
    "connector-acceptance-test",
    "responses~=0.13.3",
]

setup(
    name="source_zenloop",
    description="Source implementation for Zenloop.",
    author="Alexander Batoulis",
    author_email="alexander.batoulis@hometogo.com",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
