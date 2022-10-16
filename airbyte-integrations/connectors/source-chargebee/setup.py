#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk",
    # Install chargebee according to API doc.
    # https://apidocs.chargebee.com/docs/api?lang=python&prod_cat_ver=2#client_library
    "chargebee>=2,<3",
    "backoff==1.10.0",
    "pendulum==1.2.0",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "source-acceptance-test",
    "jsonschema~=3.2.0",
    "responses~=0.13.3",
]

setup(
    name="source_chargebee",
    description="Source implementation for Chargebee.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
