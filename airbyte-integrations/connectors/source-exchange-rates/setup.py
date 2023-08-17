#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "pendulum>=2,<3"]

TEST_REQUIREMENTS = ["pytest~=6.1", "pytest-mock~=3.6.1", "requests-mock"]


setup(
    name="source_exchange_rates",
    description="Source implementation for Exchange Rate API.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    package_data={"": ["*.json", "*.yaml", "schemas/*.json"]},
    install_requires=MAIN_REQUIREMENTS,
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
