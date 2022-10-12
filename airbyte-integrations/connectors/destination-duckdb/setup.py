#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    # "duckdb==0.5.2.dev618",
    # "git+https://github.com/duckdb/duckdb.git",
    # "duckdb @ git+https://github.com/duckdb/duckdb.git#7c111322de1095436350f95e33c5553b09302165",
    # "https://github.com/duckdb/duckdb/archive/master.tar.gz",
]

TEST_REQUIREMENTS = ["pytest~=6.1"]

setup(
    name="destination_duckdb",
    description="Destination implementation for Duckdb.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
