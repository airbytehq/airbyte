#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.2",
    "pendulum==2.1.2",
]

TEST_REQUIREMENTS = ["pytest~=6.2", "pytest-mock~=3.6.1", "source-acceptance-test", "freezegun~=1.2.2", "responses~=0.22.0"]

setup(
    name="source_assembled",
    description="Source implementation for Assembled.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
