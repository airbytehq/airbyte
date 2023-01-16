#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.2",
    "databend-sqlalchemy==0.0.9",
]

TEST_REQUIREMENTS = [
    "pytest~=6.2",
    "source-acceptance-test",
]

setup(
    name="source_databend",
    description="Source implementation for Databend.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
