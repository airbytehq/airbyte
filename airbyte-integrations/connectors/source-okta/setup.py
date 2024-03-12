#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "pendulum==1.2.0",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "pytest-mock~=3.6.1",
    "requests-mock",
]

setup(
    entry_points={
        "console_scripts": [
            "source-okta=source_okta.run:run",
        ],
    },
    name="source_okta",
    description="Source implementation for Okta.",
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
)
