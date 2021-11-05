#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "source-acceptance-test",
]

setup(
    name="google_sheets_source",
    description="Source implementation for Google Sheets.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=[
        "airbyte-protocol",
        "base-python",
        "backoff",
        "requests",
        "google-auth-httplib2",
        "google-api-python-client",
        "PyYAML==5.4",
        "pydantic==1.6.2",
    ],
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
