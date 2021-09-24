#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "cached_property~=1.5",
    "facebook_business~=11.0",
    "pendulum>=2,<3",
    "backoff",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "requests_mock==1.8.0",
]

setup(
    name="source_instagram",
    description="Source implementation for Instagram.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
