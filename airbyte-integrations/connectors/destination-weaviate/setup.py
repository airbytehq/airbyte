#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk[vector-db-based]==0.57.0", "weaviate-client==3.25.2"]

TEST_REQUIREMENTS = ["pytest~=6.2", "docker", "pytest-docker==2.0.1"]

setup(
    name="destination_weaviate",
    description="Destination implementation for Weaviate.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
