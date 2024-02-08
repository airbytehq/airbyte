#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk==0.60.1", "stripe==2.56.0", "pendulum==2.1.2"]

# we set `requests-mock~=1.11.0` to ensure concurrency is supported
TEST_REQUIREMENTS = ["pytest-mock~=3.6.1", "pytest~=6.1", "requests-mock~=1.11.0", "requests_mock~=1.8", "freezegun==1.2.2"]

setup(
    name="source_stripe",
    description="Source implementation for Stripe.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={
        "": [
            # Include yaml files in the package (if any)
            "*.yml",
            "*.yaml",
            # Include all json files in the package, up to 4 levels deep
            "*.json",
            "*/*.json",
            "*/*/*.json",
            "*/*/*/*.json",
            "*/*/*/*/*.json",
        ]
    },
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
    entry_points={
        "console_scripts": [
            "source-stripe=source_stripe.run:run",
        ],
    },
)
