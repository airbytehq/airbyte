#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk[file-based]>=0.57.5",
    "msal~=1.25.0",
    "Office365-REST-Python-Client~=2.5.2",
    "smart-open~=6.4.0",
]

TEST_REQUIREMENTS = [
    "pytest-mock~=3.6.1",
    "pytest~=6.1",
    "requests-mock~=1.11.0",
]

setup(
    name="source_microsoft_onedrive",
    description="Source implementation for Microsoft OneDrive.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
