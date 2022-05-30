#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "pygsheets==2.0.5",
    "google-auth-oauthlib==0.5.1",
    "google-api-python-client==2.47.0",
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
