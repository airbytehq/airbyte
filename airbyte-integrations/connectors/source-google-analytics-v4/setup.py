#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "PyJWT", "cryptography", "requests"]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "requests-mock",
    "pytest-mock",
    "freezegun",
]

setup(
    entry_points={
        "console_scripts": [
            "source-google-analytics-v4=source_google_analytics_v4.run:run",
        ],
    },
    name="source_google_analytics_v4",
    description="Source implementation for Google Analytics V4.",
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
