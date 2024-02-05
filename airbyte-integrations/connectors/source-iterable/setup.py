#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    "pendulum~=2.1.2",
    "python-dateutil~=2.8.2",
    "requests~=2.25",
]

TEST_REQUIREMENTS = ["requests-mock~=1.9.3", "pytest-mock~=3.6.1", "pytest~=6.1", "responses==0.23.1", "freezegun==1.1.0"]


setup(
    entry_points={
        "console_scripts": [
            "source-iterable=source_iterable.run:run",
        ],
    },
    name="source_iterable",
    description="Source implementation for Iterable.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
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
)
