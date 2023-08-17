#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "timeplus~=1.2.1",
]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_timeplus",
    description="Destination implementation for Timeplus.",
    author="Airbyte",
    author_email="jove@timeplus.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
