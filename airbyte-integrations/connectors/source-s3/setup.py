#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk>=0.51.13",
    "pyarrow==12.0.1",
    "smart-open[s3]==5.1.0",
    "wcmatch==8.4",
    "dill==0.3.4",
    "pytz",
    "fastavro==1.4.11",
    "python-snappy==0.6.1",
]

TEST_REQUIREMENTS = [
    "requests-mock~=1.9.3",
    "pytest-mock~=3.6.1",
    "pytest~=6.1",
    "pandas==2.0.3",
    "psutil",
    "pytest-order",
    "netifaces~=0.11.0",
    "docker",
    "avro==1.11.0",
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
