#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

setup(
    name="source_zoom_singer",
    description="Source implementation for Zoom, built on the Singer tap implementation.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=["airbyte-cdk", "tap-zoom==1.0.0", "pytest==6.1.2"],
    package_data={"": ["*.json"]},
)
