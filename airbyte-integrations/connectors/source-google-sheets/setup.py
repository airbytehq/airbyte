#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "backoff",
    "requests",
    "google-auth-httplib2",
    "google-api-python-client",
    "PyYAML==5.4",
    "pydantic~=1.9.2",
    "Unidecode",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "connector-acceptance-test",
]

setup(
    name="source_google_sheets",
    description="Source implementation for Google Sheets.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
