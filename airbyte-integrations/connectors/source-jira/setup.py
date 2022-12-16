#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk~=0.14", "requests==2.25.1", "pendulum~=2.1.2"]

TEST_REQUIREMENTS = [
    "pytest==6.2.5",
    "source-acceptance-test",
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
