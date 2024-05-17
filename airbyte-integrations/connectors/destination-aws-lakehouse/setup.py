#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "pandas==2.2.1",
    "awswrangler==3.6.0",
    # "awswrangler @ git+https://github.com/sharon-clue/aws-sdk-pandas@main",
    "retrying",
]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_aws_lakehouse",
    description="Destination implementation for Aws Lakehouse.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
