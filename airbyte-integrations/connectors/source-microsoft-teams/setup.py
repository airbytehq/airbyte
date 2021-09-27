#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

setup(
    name="source_microsoft_teams",
    description="Source implementation for Microsoft Teams.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=["airbyte-protocol", "base-python", "requests", "msal==1.7.0", "backoff", "pytest==6.1.2"],
    package_data={"": ["*.json", "schemas/*.json"]},
)
