#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from setuptools import find_packages, setup

setup(
    name="source_python_http_tutorial",
    description="Source implementation for Python Http Tutorial.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=["airbyte-cdk", "pytest"],
    package_data={"": ["*.json"]},
)
