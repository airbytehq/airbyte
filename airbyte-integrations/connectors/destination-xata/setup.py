#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "xata==0.10.1"]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_xata",
    description="Destination implementation for Xata.io",
    author="Philip Krauss <philip@xata.io>",
    author_email="support@xata.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
