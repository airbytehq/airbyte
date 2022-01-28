#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "backoff==1.11.1",
    "pendulum==2.1.2",
    "requests==2.26.0",
]

TEST_REQUIREMENTS = [
    "pytest==6.1.2",
    "requests_mock==1.8.0",
    "source-acceptance-test",
]

setup(
    name="source_hubspot",
    description="Source implementation for HubSpot.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
