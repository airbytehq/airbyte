#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

setup(
    name="source_appsflyer_singer",
    description="Source implementation for Appsflyer, built on the Singer tap implementation.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=[
        "tap-appsflyer @ git+https://github.com/Muriloo/tap-appsflyer",
        "airbyte-protocol",
        "base-singer",
        "base-python",
        "pytest==6.1.2",
    ],
    package_data={"": ["*.json"]},
)
