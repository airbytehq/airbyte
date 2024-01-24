#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

setup(
    name="source_broken",
    version="0.0.1",
    description="Test Soutce",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "source-broken=source_broken.run:run",
        ],
    },
)
