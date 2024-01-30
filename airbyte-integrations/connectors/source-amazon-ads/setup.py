#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "requests_oauthlib~=1.3.1", "pendulum~=2.1.2"]

TEST_REQUIREMENTS = [
    "requests-mock~=1.9.3",
    "pytest~=6.1",
    "pytest-mock~=3.7.0",
    "jsonschema~=3.2.0",
    "responses~=0.23.1",
    "freezegun~=1.2.0",
]

setup(
    entry_points={
        "console_scripts": [
            "source-amazon-ads=source_amazon_ads.run:run",
        ],
    },
    name="source_amazon_ads",
    description="Source implementation for Amazon Ads.",
    author="Airbyte",
    author_email="contact@airbyte.io",
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
