#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
    "pytest~=6.1",
]

TEST_REQUIREMENTS = [
    "pytest~=6.1",
    "pytest-mock",
    "source-acceptance-test",
]

setup(
    name="source_yandex_metrica",
    description="Source implementation for Yandex Metrica.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
