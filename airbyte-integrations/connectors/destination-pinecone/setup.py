#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "langchain",
    "openai",
    "requests",
    "tiktoken",
    "pinecone-client",
    "typing-inspect==0.8.0",
    "typing_extensions==4.5.0",
    "pydantic==1.10.8",
    "cohere",
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
