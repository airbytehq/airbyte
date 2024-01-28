#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "sgqlc"]

TEST_REQUIREMENTS = ["requests-mock~=1.9.3", "pytest-mock~=3.6.1", "pytest~=6.2", "responses~=0.23.1", "freezegun~=1.2"]

setup(
    name="source_github",
    description="Source implementation for Github.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
