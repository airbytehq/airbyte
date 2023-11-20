#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk==0.53.6", "stripe==2.56.0", "pendulum==2.1.2"]

TEST_REQUIREMENTS = ["pytest-mock~=3.6.1", "pytest~=6.1", "requests-mock", "requests_mock~=1.8", "freezegun==1.2.2"]

setup(
    name="source_stripe",
    description="Source implementation for Stripe.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
