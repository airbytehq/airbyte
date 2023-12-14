#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk==0.54.0", "pandas"]  # Pinning airbyte-cdk until we update source-salesforce to use the ConcurrentSource

TEST_REQUIREMENTS = ["freezegun", "pytest~=6.1", "pytest-mock~=3.6", "requests-mock~=1.9.3", "pytest-timeout"]

setup(
    name="source_salesforce",
    description="Source implementation for Salesforce.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
