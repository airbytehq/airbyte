#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "PyJWT==2.4.0", "cryptography==37.0.4", "requests", "pandas"]

TEST_REQUIREMENTS = [
    "freezegun",
    "pytest~=6.1",
    "pytest-mock~=3.6.1",
    "requests-mock",
]

setup(
    entry_points={
        "console_scripts": [
            "source-google-analytics-data-api=source_google_analytics_data_api.run:run",
        ],
    },
    name="source_google_analytics_data_api",
    description="Source implementation for Google Analytics Data Api.",
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
