#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "boto3"]

TEST_REQUIREMENTS = ["pytest~=6.1", "source-acceptance-test", "moto[sqs, iam]"]

setup(
    name="source_amazon_sqs",
    description="Source implementation for Amazon Sqs.",
    author="Alasdair Brown",
    author_email="airbyte@alasdairb.com",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
