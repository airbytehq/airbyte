"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-protocol",
    "base-python",
    "gcsfs==0.7.1",
    "genson==1.2.2",
    "google-cloud-storage==1.35.0",
    "pandas>=0.24.1",
    "paramiko==2.7.2",
    "s3fs==0.5.2",
    "smart-open[all]==4.1.2",
]

TEST_REQUIREMENTS = [
    "airbyte-python-test",
    "boto3==1.16.57",
    "pytest==6.1.2",
    "pytest-docker==0.10.1",
]

setup(
    name="source_file",
    description="Source implementation for File",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    extras_require={
        # Dependencies required by the main package but not integration tests should go in main. Deps required by
        # integration tests but not the main package go in integration_tests. Deps required by both should go in
        # install_requires.
        "main": [],
        "tests": TEST_REQUIREMENTS,
    },
)
