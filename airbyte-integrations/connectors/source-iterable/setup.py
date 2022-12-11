#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "pendulum~=2.1.2",
    "python-dateutil~=2.8.2",
    "requests~=2.25",
]

TEST_REQUIREMENTS = ["pytest~=6.1", "responses==0.13.3", "freezegun==1.1.0"]


setup(
    name="source_iterable",
    description="Source implementation for Iterable.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
    package_data={"": ["*.json", "schemas/*.json"]},
)
