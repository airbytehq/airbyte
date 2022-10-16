#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk~=0.1", "braintree~=4.11.0", "pendulum~=1.5.1", "inflection~=0.5.1", "backoff~=1.11.0"]

TEST_REQUIREMENTS = ["pytest~=6.1", "source-acceptance-test", "freezegun~=1.1.0", "responses~=0.13.3"]

setup(
    name="source_braintree",
    description="Source implementation for Braintree.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
