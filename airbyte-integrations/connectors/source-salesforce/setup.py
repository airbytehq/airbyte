#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "vcrpy==4.1.1"]

TEST_REQUIREMENTS = ["pytest~=6.1", "source-acceptance-test", "requests_mock", "pytest-timeout"]

setup(
    name="source_salesforce",
    description="Source implementation for Salesforce.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
