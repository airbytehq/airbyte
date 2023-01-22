#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "pendulum~=2.1.2",
    "isodate~=0.6.1",
]

TEST_REQUIREMENTS = [
    "pytest~=6.2",
    "pytest-mock~=3.6.1",
    "source-acceptance-test",
]

setup(
    name="source_railz_ai",
    description="Source implementation for Railz Ai.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
