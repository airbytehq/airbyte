#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "pika>=1.1.0",
    "threaded",
    "requests",
]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_lamatic",
    description="Destination implementation for Lamatic.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
