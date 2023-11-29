#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk[vector-db-based]==0.53.3",
    "pinecone-client[grpc]",
]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_pinecone",
    description="Destination implementation for Pinecone.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
