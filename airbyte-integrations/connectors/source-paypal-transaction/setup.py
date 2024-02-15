#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk>=0.62.0",
]

TEST_REQUIREMENTS = [
    "pytest~=8.0",
    "pytest-mock~=3.12",
    "requests-mock~=1.11",
    "selenium~=4.17.2",
]

setup(
    entry_points={
        "console_scripts": [
            "source-paypal-transaction=source_paypal_transaction.run:run",
        ],
    },
    name="source_paypal_transaction",
    description="Source implementation for Paypal Transaction.",
    author="Airbyte",
    author_email="jose.pineda@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={
        "": [
            # Include yaml files in the package (if any)
            "*.yml",
            "*.yaml",
            # Include all json files in the package, up to 4 levels deep
            "*.json",
            "*/*.json",
            "*/*/*.json",
            "*/*/*/*.json",
            "*/*/*/*/*.json",
        ]
    },
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
