#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "pendulum~=2.1.2",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "pytest-mock~=3.6.1",
    "pytest-cov",
    "source-acceptance-test",
]

setup(
    name="source_open_exchange_rates",
    description="Source implementation for Open Exchange Rates.",
    author="Airbyte",
    author_email="marc@marketparts.com",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
