#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import setuptools

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1.56",
    "docker~=5.0.3",
    "PyYAML~=5.4",
    "icdiff~=1.9",
    "inflection~=0.5",
    "pdbpp~=0.10",
    "pydantic~=1.6",
    "pytest~=6.1",
    "pytest-sugar~=0.9",
    "pytest-timeout~=1.4",
    "pprintpp~=0.4",
    "dpath~=2.0.1",
    "jsonschema~=3.2.0",
    "jsonref==0.2",
    "requests-mock",
    "pytest-mock~=3.6.1",
]

setuptools.setup(
    name="source-acceptance-test",
    description="Contains acceptance tests for source connectors.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    url="https://github.com/airbytehq/airbyte",
    packages=setuptools.find_packages(),
    install_requires=MAIN_REQUIREMENTS,
)
