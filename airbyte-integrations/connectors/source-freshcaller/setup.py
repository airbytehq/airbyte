#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "pendulum==1.2.0",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "pytest-mock~=3.6.1",
    "requests-mock~=1.9.3",
    "source-acceptance-test",
]

setup(
    name="source_freshcaller",
    description="Source implementation for Freshcaller.",
    author="Jay Bujala (Snapcommerce)",
    author_email="jay.bujala@snapcommerce.com",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
