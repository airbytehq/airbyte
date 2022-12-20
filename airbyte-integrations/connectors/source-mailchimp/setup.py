#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

TEST_REQUIREMENTS = ["pytest~=6.1", "source-acceptance-test", "responses~=0.19.0", "requests-mock~=1.9.3"]


setup(
    name="source_mailchimp",
    description="Source implementation for Mailchimp.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=[
        "airbyte-cdk",
        "pytest~=6.1",
    ],
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={"tests": TEST_REQUIREMENTS},
)
