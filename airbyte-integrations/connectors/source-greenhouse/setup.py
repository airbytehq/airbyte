#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

TEST_REQUIREMENTS = [
    "requests-mock~=1.9.3",
    "pytest~=6.1",
    "pytest-mock~=3.6",
]

setup(
    entry_points={
        "console_scripts": [
            "source-greenhouse=source_greenhouse.run:run",
        ],
    },
    name="source_greenhouse",
    description="Source implementation for Greenhouse.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=["airbyte-cdk>=0.44.1", "dataclasses-jsonschema==2.15.1"],
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
