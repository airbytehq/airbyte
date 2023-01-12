#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.19",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "pytest-mock~=3.6.1",
    "source-acceptance-test",
]

DISCOVER_REQUIREMENTS = [
    "beautifulsoup4~=4.11.1",
    "html5lib~=1.1",
    "pandas~=1.5.2",
]

setup(
    name="source_exact",
    description="Source implementation for Exact.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
        "discover": DISCOVER_REQUIREMENTS,
    },
)
