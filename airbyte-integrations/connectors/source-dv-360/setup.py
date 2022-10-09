#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk~=0.1", "google-api-python-client"]

TEST_REQUIREMENTS = ["pytest~=6.1", "source-acceptance-test", "pytest-mock"]

setup(
    name="source_dv_360",
    description="Source implementation for Display & Video 360.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
