#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk", "pydantic==1.9.0", "psycopg2==2.9.3", "dotmap==1.3.26", "boto3==1.21.0"
]

TEST_REQUIREMENTS = [
    "pytest~=6.1"
]

setup(
    name="destination_redshift_py",
    description="Destination implementation for Redshift Py.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
