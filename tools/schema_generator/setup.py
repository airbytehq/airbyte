#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte_cdk==0.1.60", "genson==1.2.2"]

TEST_REQUIREMENTS = ["pytest"]


setup(
    version="0.1.0",
    name="schema_generator",
    description="Util to create catalog schemas for an Airbyte Connector.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
    python_requires=">=3.9",
    entry_points={
        "console_scripts": ["schema_generator = schema_generator.main:main"],
    },
)
