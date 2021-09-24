#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

setup(
    name="source_sendgrid",
    description="Source implementation for Sendgrid.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=["airbyte-cdk~=0.1", "backoff", "requests", "pytest==6.1.2", "pytest-mock"],
    package_data={"": ["*.json", "schemas/*.json"]},
)
