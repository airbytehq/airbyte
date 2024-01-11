#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "google-api-python-client",
    "google-auth",
]

TEST_REQUIREMENTS = [
    "pytest-mock~=3.6.1",
    "pytest~=6.1",
    "pytest-lazy-fixture",
    "requests-mock",
]

setup(
    entry_points={
        "console_scripts": [
            "source-google-search-console=source_google_search_console.run:run",
        ],
    },
    name="source_google_search_console",
    description="Source implementation for Google Search Console.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
