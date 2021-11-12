#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import setuptools

setuptools.setup(
    name="airbyte-python-test",
    description="Contains classes for running integration tests.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    url="https://github.com/airbytehq/airbyte",
    packages=setuptools.find_packages(),
    install_requires=["airbyte-protocol"],
    entry_points={
        "console_scripts": ["airbyte-python-test=base_python_test.standard_test:main"],
    },
)
