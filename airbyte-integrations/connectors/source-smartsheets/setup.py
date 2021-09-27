#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

setup(
    name="source_smartsheets",
    description="Source implementation for Smartsheets.",
    author="Nate Nowack",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=["airbyte-cdk-test", "pytest==6.1.2", "smartsheet-python-sdk"],
    package_data={"": ["*.json"]},
)
