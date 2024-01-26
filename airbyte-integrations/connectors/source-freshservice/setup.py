#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.55.2",
]

TEST_REQUIREMENTS = ["pytest~=6.2", "pytest-mock~=3.6.1"]

setup(
    entry_points={
        "console_scripts": [
            "source-freshservice=source_freshservice.run:run",
        ],
    },
    name="source_freshservice",
    description="Source implementation for Freshservice.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
