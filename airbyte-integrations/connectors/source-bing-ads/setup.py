#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "bingads~=13.0.13", "vcrpy==4.1.1", "backoff==1.10.0", "pendulum==2.1.2"]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "source-acceptance-test",
]

setup(
    name="source_bing_ads",
    description="Source implementation for Bing Ads.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
