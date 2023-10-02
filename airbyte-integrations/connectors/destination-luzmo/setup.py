#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "luzmo-sdk"]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_luzmo",
    description="Airbyte destination connector implementation for Luzmo.",
    author="Luzmo",
    author_email="support@luzmo.com",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
