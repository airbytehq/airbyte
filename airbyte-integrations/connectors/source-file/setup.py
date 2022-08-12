#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "gcsfs==2022.7.1",
    "genson==1.2.2",
    "google-cloud-storage==2.5.0",
    "pandas==1.4.3",
    "paramiko==2.11.0",
    "s3fs==2022.7.1",
    "boto3==1.21.21",
    "smart-open[all]==6.0.0",
    "lxml==4.9.1",
    "html5lib==1.1",
    "beautifulsoup4==4.11.1",
    "pyarrow==9.0.0",
    "xlrd==2.0.1",
    "openpyxl==3.0.10",
    "pyxlsb==1.0.9",
]

TEST_REQUIREMENTS = ["pytest~=6.2", "pytest-docker==1.0.0", "pytest-mock~=3.6.1"]

setup(
    name="source_file",
    description="Source implementation for File",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
