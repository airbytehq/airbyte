#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk~=0.2", "mimesis==6.1.1"]

TEST_REQUIREMENTS = [
    "requests-mock~=1.9.3",
    "pytest-mock~=3.6.1",
    "pytest~=6.2",
]

setup(
    name="source_faker",
    description="Source implementation for fake but realistic looking data.",
    author="Airbyte",
    author_email="evan@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "record_data/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
