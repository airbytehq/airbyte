#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk @ git+https://git@github.com/airbytehq/airbyte.git@grubberr/17919-airbyte_cdk#egg=airbyte_cdk&subdirectory=airbyte-cdk/python",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "pytest-mock~=3.6.1",
    "requests-mock~=1.9.3",
    "source-acceptance-test",
]

setup(
    name="source_linnworks",
    description="Source implementation for Linnworks.",
    author="Labanoras Tech",
    author_email="jv@labanoras.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
