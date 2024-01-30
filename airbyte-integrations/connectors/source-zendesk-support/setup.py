#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "pytz"]

TEST_REQUIREMENTS = ["freezegun", "pytest~=6.1", "pytest-mock~=3.6", "requests-mock==1.9.3"]

setup(
    entry_points={
        "console_scripts": [
            "source-zendesk-support=source_zendesk_support.run:run",
        ],
    },
    version="0.1.0",
    name="source_zendesk_support",
    description="Source implementation for Zendesk Support.",
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
