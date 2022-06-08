#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "tap-quickbooks @ https://github.com/airbytehq//tap-quickbooks/tarball/v1.0.5-airbyte",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
]

setup(
    name="source_quickbooks_singer",
    description="Source implementation for QuickBooks, built on the Singer tap implementation.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
