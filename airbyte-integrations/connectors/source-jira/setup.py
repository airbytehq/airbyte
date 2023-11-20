#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk>=0.51.19"]

TEST_REQUIREMENTS = [
    "requests-mock~=1.9.3",
    "pytest-mock~=3.6.1",
    "pytest==6.2.5",
    "responses~=0.22.0",
]

setup(
    name="source_jira",
    description="Source implementation for Jira.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
