#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

setup(
    name="source_appstore_singer",
    description="Source implementation for Appstore, built on the Singer tap implementation.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=[
        "airbyte-protocol",
        "appstoreconnect==0.9.0",
        "base-singer",
        "base-python",
        "pyjwt==1.6.4",  # required by appstore connect
        "pytest==6.1.2",
        "tap-appstore @ https://github.com/airbytehq/tap-appstore/tarball/v0.2.1-airbyte",
    ],
    package_data={"": ["*.json"]},
)
