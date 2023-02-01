#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.2",
    "paramiko==2.11.0",
    "backoff==1.8.0",
    "terminaltables==3.1.0",
    "pandas==1.5.0",
]

TEST_REQUIREMENTS = ["pytest~=6.1", "source-acceptance-test", "docker==5.0.3"]

setup(
    name="source_sftp_bulk",
    description="Source implementation for SFTP Bulk.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
