#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk~=0.1"]

TEST_REQUIREMENTS = ["requests-mock~=1.9.3", "pytest~=6.1", "pytest-mock", "requests_mock~=1.8"]

setup(
    name="source_klaviyo",
    description="Source implementation for Klaviyo.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
