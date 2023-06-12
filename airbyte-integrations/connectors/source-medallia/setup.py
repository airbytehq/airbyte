#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.2",
    "sgqlc~=16.0",
]

TEST_REQUIREMENTS = [
    "pytest~=6.2",
    "connector-acceptance-test",
]

setup(
    name="source_medallia",
    description="Source implementation for Medallia.",
    author="James Gould",
    author_email="james.gould@sonos.com",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
