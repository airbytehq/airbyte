#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "smart_open==5.1.0", "paramiko==2.10.1"]

TEST_REQUIREMENTS = ["pytest~=6.1", "docker==5.0.3"]

setup(
    name="destination_sftp_json",
    description="Destination implementation for Sftp Json.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
