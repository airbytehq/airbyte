#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "paramiko==2.9.2",
    "pytz==2021.3",
    "pandas==1.3.5",
    "backoff==1.11.1"
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "source-acceptance-test",
]

setup(
    name="source_sftp",
    description="Source implementation for SFTP.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
