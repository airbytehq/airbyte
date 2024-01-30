#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk", "boto3"]

TEST_REQUIREMENTS = ["requests-mock~=1.9.3", "pytest-mock~=3.6.1", "pytest~=6.1", "moto[sqs, iam]"]

setup(
    entry_points={
        "console_scripts": [
            "source-amazon-sqs=source_amazon_sqs.run:run",
        ],
    },
    name="source_amazon_sqs",
    description="Source implementation for Amazon Sqs.",
    author="Alasdair Brown",
    author_email="airbyte@alasdairb.com",
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
