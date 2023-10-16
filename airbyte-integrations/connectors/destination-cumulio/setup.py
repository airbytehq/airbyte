#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "cumulio"]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_cumulio",
    description="Airbyte destination connector implementation for Cumul.io.",
    author="Cumul.io",
    author_email="support@cumul.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
