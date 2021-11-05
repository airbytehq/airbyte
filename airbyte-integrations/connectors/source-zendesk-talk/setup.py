#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-protocol",
    "base-python",
    "backoff==1.10.0",
    "pendulum==1.2.0",
    "requests==2.25.1",
]

TEST_REQUIREMENTS = ["pytest", "requests_mock==1.8.0"]


setup(
    name="source_zendesk_talk",
    description="Source implementation for Zendesk Talk.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS + TEST_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json"]},
)
