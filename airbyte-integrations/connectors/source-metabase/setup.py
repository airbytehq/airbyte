#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "requests>=2.28.0", "types-requests>=2.27.30"]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "requests-mock",
    "requests_mock~=1.8",
]

setup(
    name="source_metabase",
    description="Source implementation for Metabase.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
