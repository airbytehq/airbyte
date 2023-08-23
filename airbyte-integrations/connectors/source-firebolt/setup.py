#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "firebolt-sdk>=0.14.0"]

TEST_REQUIREMENTS = [
    "requests-mock~=1.9.3",
    "pytest-mock~=3.6.1",
    "pytest>=6.2.5",  # 6.2.5 has python10 compatibility fixes
    "pytest-asyncio>=0.18.0",
]

setup(
    name="source_firebolt",
    description="Source implementation for Firebolt.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
