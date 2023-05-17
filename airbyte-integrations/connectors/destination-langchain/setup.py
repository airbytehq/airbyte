#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "langchain",
    "openai",
    "weaviate-client",
    "requests",
    "tiktoken"
]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_langchain",
    description="Destination implementation for Langchain.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
