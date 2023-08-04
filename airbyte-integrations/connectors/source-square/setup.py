#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk>=0.44.2",
]

TEST_REQUIREMENTS = [
    "freezegun",
    "pytest~=6.1",
    "pytest-mock~=3.6.1",
    "connector-acceptance-test",
]

setup(
    name="source_square",
    description="Source implementation for Square.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
