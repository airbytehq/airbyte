#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

setup(
    name="source_mailchimp",
    description="Source implementation for Mailchimp.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=[
        "airbyte-cdk~=0.1.35",
        "pytest~=6.1",
    ],
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={"tests": ["pytest~=6.1"]},
)
