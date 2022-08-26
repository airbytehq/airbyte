#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "gcsfs==0.7.1",
    "genson==1.2.2",
    "google-cloud-storage==1.35.0",
    "pandas==1.4.3",
    "paramiko==2.7.2",
    "s3fs==0.4.2",
    "smart-open[all]==4.1.2",
    "lxml==4.6.5",
    "html5lib==1.1",
    "beautifulsoup4==4.9.3",
    "pyarrow==8.0.0",
    "xlrd==2.0.1",
    "openpyxl==3.0.6",
    "pyxlsb==1.0.8",
]

TEST_REQUIREMENTS = [
    "boto3==1.16.57",
    "pytest==6.1.2",
    "pytest-docker==0.10.1",
]

setup(
    name="source_file_secure",
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
