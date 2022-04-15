#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "pygsheets",
    "google-auth-oauthlib",
    "google-api-python-client",
]

TEST_REQUIREMENTS = ["pytest~=6.1", "requests-mock"]

setup(
    name="destination_google_sheets",
    description="Destination implementation for Google Sheets.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
