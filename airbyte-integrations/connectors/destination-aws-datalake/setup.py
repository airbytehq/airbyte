#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "retrying",
    "awswrangler==2.16.1",
    "pandas==1.4.4",
]

TEST_REQUIREMENTS = ["pytest~=6.1"]

setup(
    name="destination_aws_datalake",
    description="Destination implementation for Aws Datalake.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
