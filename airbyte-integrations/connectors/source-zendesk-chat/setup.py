#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-protocol",
    "base-python",
    "pendulum==1.2.0",
    "requests==2.25.1",
]

TEST_REQUIREMENTS = ["pytest==6.1.2", "source-acceptance-test"]

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
