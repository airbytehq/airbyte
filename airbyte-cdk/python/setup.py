#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import pathlib

from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="airbyte-cdk",
    version="0.1.62",
    description="A framework for writing Airbyte Connectors.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Airbyte",
    author_email="contact@airbyte.io",
    license="MIT",
    url="https://github.com/airbytehq/airbyte",
    classifiers=[
        # This information is used when browsing on PyPi.
        # Dev Status
        "Development Status :: 3 - Alpha",
        # Project Audience
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        # Python Version Support
        "Programming Language :: Python :: 3.9",
    ],
    keywords="airbyte connector-development-kit cdk",
    project_urls={
        "Documentation": "https://docs.airbyte.io/",
        "Source": "https://github.com/airbytehq/airbyte",
        "Tracker": "https://github.com/airbytehq/airbyte/issues",
    },
    packages=find_packages(exclude=("unit_tests",)),
    install_requires=[
        "backoff",
        "dpath~=2.0.1",
        "jsonschema~=3.2.0",
        "jsonref~=0.2",
        "pendulum",
        "pydantic~=1.6",
        "PyYAML~=5.4",
        "requests",
        "vcrpy",
        "Deprecated~=1.2",
        "Jinja2~=3.1.2",
        "jello~=1.5.2",
    ],
    python_requires=">=3.9",
    extras_require={
        "dev": [
            "MyPy~=0.812",
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "requests-mock",
            "pytest-httpserver",
        ],
        "sphinx-docs": [
            "Sphinx~=4.2",
            "sphinx-rtd-theme~=1.0",
        ],
    },
)
