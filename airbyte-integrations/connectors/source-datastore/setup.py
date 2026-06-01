#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from setuptools import find_packages, setup


MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "google-cloud-datastore>=2.19",
    "google-auth>=2.28",
]

TEST_REQUIREMENTS = [
    "mock",
    "pytest~=6.2",
    "pytest-mock~=3.6",
]

setup(
    name="source_datastore",
    description="Source implementation for Google Cloud Datastore.",
    author="Jeremy Juventin",
    author_email="jeremy.juventin@prestashop.com",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
