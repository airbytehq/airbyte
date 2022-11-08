#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk~=0.1", "boto3~=1.16", "pendulum~=2.1", "pycryptodome~=3.10", "xmltodict~=0.12"]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "pytest-mock",
]

setup(
    name="source_amazon_seller_partner",
    description="Source implementation for Amazon Seller Partner.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
