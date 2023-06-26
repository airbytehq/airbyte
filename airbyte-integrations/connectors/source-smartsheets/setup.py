#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "smartsheet-python-sdk==2.177.1", "urllib3<2.0"]
TEST_REQUIREMENTS = ["pytest", "pytest-mock~=3.6.1"]

setup(
    name="source_smartsheets",
    description="Source implementation for Smartsheets.",
    author="Nate Nowack",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
    package_data={"": ["*.json"]},
)
