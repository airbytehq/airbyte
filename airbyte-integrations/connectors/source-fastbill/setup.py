#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.4",
]

TEST_REQUIREMENTS = ["pytest~=6.1", "pytest-mock~=3.6.1", "source-acceptance-test", "responses~=0.21.0"]

setup(
    name="source_fastbill",
    description="Source implementation for Fastbill.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
