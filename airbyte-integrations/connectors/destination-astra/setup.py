#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk==0.55.1",
    "langchain==0.0.271",
    "openai==0.27.9",
    "tiktoken==0.4.0",
]

TEST_REQUIREMENTS = ["pytest~=6.2"]

setup(
    name="destination_astra",
    description="Destination implementation for Astra.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
