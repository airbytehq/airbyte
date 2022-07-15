#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "Salesforce-FuelSDK-Sans",
    "tap-exacttarget-remove-sud==1.7.4",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
]

setup(
    name="source_sf_marketingcloud_singer",
    description="Source implementation for Sf Marketingcloud, built on the Singer tap implementation.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
