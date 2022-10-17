#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk @ git+https://git@github.com/airbytehq/airbyte.git@grubberr/17919-airbyte_cdk#egg=airbyte_cdk&subdirectory=airbyte-cdk/python",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "pytest-mock~=3.6.1",
    "source-acceptance-test",
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
