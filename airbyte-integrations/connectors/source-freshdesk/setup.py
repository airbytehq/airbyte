#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-protocol",
    "base-python",
    "backoff==1.10.0",
    "requests==2.25.1",
    "pendulum==2.1.2",
]

TEST_REQUIREMENTS = [
    "pytest==6.1.2",
    "requests_mock==1.8.0",
]

setup(
    name="source_freshdesk",
    description="Source implementation for Freshdesk.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
