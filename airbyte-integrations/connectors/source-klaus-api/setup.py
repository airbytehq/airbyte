#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.2",
]

TEST_REQUIREMENTS = [
    "pytest~=6.2",
    "pytest-mock~=3.6.1",
]

setup(
    entry_points={
        "console_scripts": [
            "source-klaus-api=source_klaus_api.run:run",
        ],
    },
    name="source_klaus_api",
    description="Source implementation for Klaus Api.",
    author="Deke Li",
    author_email="deke.li@sendinblue.com",
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
