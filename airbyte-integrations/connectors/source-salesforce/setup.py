#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk~=0.2", "vcrpy==4.1.1", "pandas"]

TEST_REQUIREMENTS = ["pytest~=6.1", "pytest-mock~=3.6", "requests_mock", "connector-acceptance-test", "pytest-timeout"]

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
