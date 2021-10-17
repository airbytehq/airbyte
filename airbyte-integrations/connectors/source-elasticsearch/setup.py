#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    # elasticsearch >= 7.14 does not support non-official clusters (e.g. AWS)
    "elasticsearch<7.14",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "source-acceptance-test",
]

setup(
    name="source_elasticsearch",
    description="Source implementation for Elasticsearch.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
