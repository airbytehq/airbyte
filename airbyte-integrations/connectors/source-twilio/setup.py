#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "pendulum",
    "requests",
]

TEST_REQUIREMENTS = ["requests-mock~=1.9.3", "pytest~=6.1", "pytest-mock", "requests_mock", "freezegun"]

setup(
    entry_points={
        "console_scripts": [
            "source-twilio=source_twilio.run:run",
        ],
    },
    name="source_twilio",
    description="Source implementation for Twilio.",
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
