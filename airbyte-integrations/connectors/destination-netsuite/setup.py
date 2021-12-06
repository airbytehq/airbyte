#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "httpx",
    "asyncio",
    "authlib",
    "oauthlib",
    "pydantic",
    "pytest",
    "pytest-asyncio"    
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
]

setup(
    name="destination_netsuite",
    description="Destination implementation for Netsuite.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
