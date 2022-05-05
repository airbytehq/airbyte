#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk~=0.1", "backoff", "requests"]

TEST_REQUIREMENTS = ["pytest==6.1.2", "pytest-mock"]

setup(
    name="source_sendgrid",
    description="Source implementation for Sendgrid.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
