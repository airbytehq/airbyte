#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "pendulum==1.2.0",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "source-acceptance-test",
    "pytest-mock~=3.6.1",
    "requests-mock",
]

setup(
    name="source_okta",
    description="Source implementation for Okta.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
