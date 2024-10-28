#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from setuptools import find_packages, setup

setup(
    entry_points={
        "console_scripts": [
            "source-python-http-tutorial=source_python_http_tutorial.run:run",
        ],
    },
    name="source_python_http_tutorial",
    description="Source implementation for Python Http Tutorial.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=["airbyte-cdk", "pytest"],
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
