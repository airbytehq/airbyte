#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk>=0.58.8",  # previous versions had a bug with http_method value from the manifest
]

TEST_REQUIREMENTS = [
    "requests-mock~=1.9.3",
    "pytest",
    "pytest-mock",
]

setup(
    entry_points={
        "console_scripts": [
            "source-intercom=source_intercom.run:run",
        ],
    },
    name="source_intercom",
    description="Source implementation for Intercom Yaml.",
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
