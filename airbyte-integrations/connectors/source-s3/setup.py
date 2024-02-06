#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk[file-based]>=0.60.1",
    "smart-open[s3]==5.1.0",
    "wcmatch==8.4",
    "dill==0.3.4",
    "pytz",
    "python-snappy==0.6.1",
]

# temporarily pin moto due to use of `mock_sts`, which has been deprecated
TEST_REQUIREMENTS = ["requests-mock~=1.9.3", "pytest-mock~=3.6.1", "pytest~=6.1", "pandas==2.0.3", "docker", "moto==4.2.14"]

setup(
    name="source_s3",
    description="Source implementation for S3.",
    author="Airbyte",
    author_email="contact@airbyte.io",
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
    entry_points={
        "console_scripts": [
            "source-s3=source_s3.run:run",
        ],
    },
)
