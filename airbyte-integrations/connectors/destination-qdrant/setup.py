#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk[vector-db-based]==0.53.3", "qdrant-client", "fastembed"]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_qdrant",
    description="Destination implementation for Qdrant.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
