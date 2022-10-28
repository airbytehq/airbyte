#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "pendulum >= 2,<3",
    "requests==2.25.1",
]

TEST_REQUIREMENTS = ["pytest~=6.1", "pytest-mock", "requests_mock"]

setup(
    name="source_zendesk_chat",
    description="Source implementation for Zendesk Chat.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
