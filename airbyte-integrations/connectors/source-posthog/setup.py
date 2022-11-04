#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.5.4",
    "dataclasses-jsonschema==2.15.1"
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "source-acceptance-test",
]

setup(
    name="source_posthog",
    description="Source implementation for Posthog.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json"]},
    extras_require={"tests": TEST_REQUIREMENTS},
)
