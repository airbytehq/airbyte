#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

setup(
    name="source_marketo_singer",
    description="Source implementation for Marketo, built on the Singer tap implementation.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=["airbyte-protocol", "base-singer", "base-python", "tap-marketo==2.4.1", "pytest==6.1.2"],
    package_data={"": ["*.json"]},
)
