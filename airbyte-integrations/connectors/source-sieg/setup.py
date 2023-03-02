#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from setuptools import find_packages, setup

setup(
    name="source_sieg",
    description="Source implementation for Sieg API.",
    author="Marcelo Guimaraes",
    author_email="marcelofelippe.mfg@gmail.com",
    packages=find_packages(),
    install_requires=["airbyte-cdk", "pytest==6.1.2"],
    package_data={"": ["*.json"]},
)
