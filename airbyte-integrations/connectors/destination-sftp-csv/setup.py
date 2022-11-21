#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.2",
    "paramiko==2.11.0",
    "backoff==1.8.0",
    "pandas==1.5.0",
]

TEST_REQUIREMENTS = ["pytest~=6.1", "docker==5.0.3"]

setup(
    name="destination_sftp_csv",
    description="Destination implementation for Sftp Csv.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
