#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk[file-based]>=0.53.5",
    "google-api-python-client==2.104.0",
    "google-auth-httplib2==0.1.1",
    "google-auth-oauthlib==1.1.0",
    "google-api-python-client-stubs==1.18.0",
]

TEST_REQUIREMENTS = [
    "pytest-mock~=3.6.1",
    "pytest~=6.1",
]

setup(
    name="source_google_drive",
    description="Source implementation for Google Drive.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
