#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk~=0.2", "firebolt-sdk>=0.12.0"]

TEST_REQUIREMENTS = [
    "pytest>=6.2.5",  # 6.2.5 has python10 compatibility fixes
    "pytest-asyncio>=0.18.0",
    "source-acceptance-test",
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
