#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk>=0.58.8",  # previous versions had a bug with http_method value from the manifest
]

TEST_REQUIREMENTS = [
    "requests-mock~=1.9.3",
    "pytest",
    "pytest-mock",
]

setup(
    name="source_intercom",
    description="Source implementation for Intercom Yaml.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
