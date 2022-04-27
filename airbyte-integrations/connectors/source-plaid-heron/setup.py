#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "plaid-python"
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "source-acceptance-test",
]

setup(
    name="source_plaid_heron",
    description="Source implementation for Plaid Heron. Plaid transactions are passed to Heron "
                "for categorisation and Category stream addition",
    author="Ahmed Buksh",
    author_email="ahmed.buksh@cogentlabs.co",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
