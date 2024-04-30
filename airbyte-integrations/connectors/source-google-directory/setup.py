#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    # Lastest working version was 0.42.0. May work up to 0.84 where from airbyte_cdk.sources.deprecated is removed
    "airbyte-cdk~=0.1, <0.84",
    "google-api-python-client==1.12.8",
    "google-auth-httplib2==0.0.4",
    "google-auth-oauthlib==0.4.2",
    "backoff==1.10.0",
]

TEST_REQUIREMENTS = [
    "requests-mock~=1.9.3",
    "pytest~=6.1",
    "pytest-mock~=3.6.1",
]

setup(
    entry_points={
        "console_scripts": [
            "source-google-directory=source_google_directory.run:run",
        ],
    },
    name="source_google_directory",
    description="Source implementation for Google Directory.",
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
