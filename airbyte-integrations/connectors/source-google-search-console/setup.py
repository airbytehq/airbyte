#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "google-api-python-client",
    "google-auth",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "requests-mock",
    "source-acceptance-test",
]

setup(
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
