#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

setup(
    name="source_google_directory",
    description="Source implementation for Google Directory.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=[
        "airbyte-protocol",
        "base-python",
        "google-api-python-client==1.12.8",
        "google-auth-httplib2==0.0.4",
        "google-auth-oauthlib==0.4.2",
        "backoff==1.10.0",
    ],
    package_data={"": ["*.json", "schemas/*.json"]},
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    extras_require={
        # Dependencies required by the main package but not integration tests should go in main. Deps required by
        # integration tests but not the main package go in tests. Deps required by both should go in
        # install_requires.
        "tests": ["airbyte-python-test", "pytest"],
    },
)
