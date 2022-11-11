#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk~=0.1.68", "requests_oauthlib~=1.3.1", "pendulum~=2.1.2"]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "pytest-mock~=3.7.0",
    "jsonschema~=3.2.0",
    "responses~=0.13.3",
    "freezegun~=1.2.0",
]

setup(
    name="source_amazon_ads",
    description="Source implementation for Amazon Ads.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
