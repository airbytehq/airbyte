#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "google-cloud-storage==1.17.0",
    "wget==3.2"
]

TEST_REQUIREMENTS = [
    "pytest~=6.1"
]

setup(
    name="destination_ngpvan",
    description="Destination implementation for Ngpvan.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
