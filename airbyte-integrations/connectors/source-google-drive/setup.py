#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk>=0.51.17",
    "google-api-python-client==2.104.0",
    "google-auth-httplib2==0.1.1",
    "google-auth-oauthlib==1.1.0",
    "google-api-python-client-stubs==1.18.0"
]

setup(
    name="source_google_drive",
    description="Source implementation for Google Drive.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
)
