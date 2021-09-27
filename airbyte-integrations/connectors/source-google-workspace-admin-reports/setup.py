#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

setup(
    name="source_google_workspace_admin_reports",
    description="Source implementation for Google Workspace Admin Reports.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=[
        "airbyte-protocol",
        "base-python",
        "pytest==6.1.2",
        "google-api-python-client==2.0.2",
        "google-auth-httplib2==0.1.0",
        "google-auth-oauthlib==0.4.3",
        "backoff==1.10.0",
        "pendulum==2.1.2",
    ],
    package_data={"": ["*.json", "schemas/*.json"]},
)
