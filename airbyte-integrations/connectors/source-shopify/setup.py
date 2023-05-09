#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "sgqlc~=16.0"]

TEST_REQUIREMENTS = [
    "pytest",
    "pytest-mock",
    "requests-mock",
    "connector-acceptance-test",
]

setup(
    name="source_shopify",
    description="Source CDK implementation for Shopify.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
