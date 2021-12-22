#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk~=0.1.36", "pytz"]

TEST_REQUIREMENTS = ["pytest~=6.1", "source-acceptance-test", "requests-mock==1.9.3"]

setup(
    version="0.1.0",
    name="source_zendesk_support",
    description="Source implementation for Zendesk Support.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
