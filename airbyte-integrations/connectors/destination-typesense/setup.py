#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "typesense>=0.14.0"]

TEST_REQUIREMENTS = ["pytest~=6.1", "typesense>=0.14.0"]

setup(
    name="destination_typesense",
    description="Destination implementation for Typesense.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
