#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.51.0",
    "requests",
]

TEST_REQUIREMENTS = [
    "airbyte-cdk~=0.51.0",
    "requests-mock~=1.9.3",
    "pytest~=6.2",
    "pytest-mock~=3.6.1",
    "connector-acceptance-test",
]

setup(
    name="source_gainsight_cs",
    description="Source implementation for Gainsight Cs.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
