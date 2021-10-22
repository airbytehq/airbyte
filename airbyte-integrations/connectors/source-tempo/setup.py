#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-protocol",
    "base-python",
    "airbyte-cdk"
]

TEST_REQUIREMENTS = [
    "pytest~=6.1"
]

setup(
    name="source_tempo",
    description="Source implementation for Tempo.",
    author="Thomas van Latum",
    author_email="thomas@gcompany.nl",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
