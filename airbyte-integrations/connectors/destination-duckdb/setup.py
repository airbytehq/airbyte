#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "duckdb"]  # duckdb added manually to dockerfile due to lots of errors

TEST_REQUIREMENTS = ["pytest~=6.1"]

setup(
    name="destination_duckdb",
    description="Destination implementation for Duckdb.",
    author="Simon Späti",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
