#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk~=0.1", "requests==2.25.1", "pendulum>=1.2.0", "vcrpy==4.1.1"]

TEST_REQUIREMENTS = [
    "pytest==6.1.2",
    "source-acceptance-test",
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
