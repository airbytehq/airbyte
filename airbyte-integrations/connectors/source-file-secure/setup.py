#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from pathlib import Path

from setuptools import find_packages, setup


def local_dependency(name: str) -> str:
    """Returns a path to a local package."""
    if os.environ.get("DAGGER_BUILD"):
        return f"{name} @ file:///local_dependencies/{name}"
    else:
        return f"{name} @ file://{Path.cwd().parent / name}"


MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "gcsfs==2022.7.1",
    "genson==1.2.2",
    "google-cloud-storage==2.5.0",
    "pandas==1.4.3",
    "paramiko==2.11.0",
    "s3fs==2022.7.1",
    "smart-open[all]==6.0.0",
    "lxml==4.9.1",
    "html5lib==1.1",
    "beautifulsoup4==4.11.1",
    "pyarrow==9.0.0",
    "xlrd==2.0.1",
    "openpyxl==3.0.10",
    "pyxlsb==1.0.9",
]

if not os.environ.get("DOCKER_BUILD"):
    MAIN_REQUIREMENTS.append(local_dependency("source-file"))

TEST_REQUIREMENTS = ["boto3==1.21.21", "pytest==7.1.2", "pytest-docker==1.0.0", "pytest-mock~=3.8.2"]

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
