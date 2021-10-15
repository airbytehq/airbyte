#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1.7",
    "pyarrow==4.0.1",
    "smart-open[s3]==5.1.0",
    "wcmatch==8.2",
    "dill==0.3.4",
    "pytz",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "source-acceptance-test",
    "pandas==1.3.1",
]

setup(
    name="source_s3",
    description="Source implementation for S3.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
