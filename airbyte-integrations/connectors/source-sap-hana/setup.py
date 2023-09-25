#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.2",
    "hdbcli~=2.17",
]

TEST_REQUIREMENTS = [
    "pytest~=6.2",
    "docker~=6.1",
    "pyaml~=6.0",
    "connector-acceptance-test",

]

setup(
    name="source_sap_hana",
    description="Source implementation for Sap Hana.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
