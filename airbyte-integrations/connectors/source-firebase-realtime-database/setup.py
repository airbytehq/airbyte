#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "firebase-admin",
]

TEST_REQUIREMENTS = [
    "requests-mock~=1.9.3",
    "pytest-mock~=3.6.1",
    "pytest~=6.1",
    "source-acceptance-test",
]

setup(
    entry_points={
        "console_scripts": [
            "source-firebase-realtime-database=source_firebase_realtime_database.run:run",
        ],
    },
    name="source_firebase_realtime_database",
    description="Source implementation for Firebase Realtime Database.",
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
