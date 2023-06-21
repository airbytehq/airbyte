#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.36",
    "cached_property==1.5.2",
    "facebook_business==16.0.0",
    "pendulum>=2,<3",
]

TEST_REQUIREMENTS = ["pytest~=6.1", "pytest-mock~=3.6", "requests_mock~=1.8", "freezegun"]

setup(
    name="source_facebook_marketing",
    description="Source implementation for Facebook Marketing.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
