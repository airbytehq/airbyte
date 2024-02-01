#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import setup

setup(
    name="airbyte-source-broken",
    version="0.0.1",
    description="Test Soutce",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=["source_broken"],
    entry_points={
        "console_scripts": [
            "source-broken=source_broken.run:run",
        ],
    },
)
