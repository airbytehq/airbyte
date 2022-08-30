#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
import pathlib

from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="octavia-cli",
    version="0.40.3",
    description="A command line interface to manage Airbyte configurations",
    long_description=README,
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
        "Programming Language :: Python :: 3.8",
    ],
    keywords="airbyte cli command-line-interface configuration",
    project_urls={
        "Documentation": "https://docs.airbyte.io/",
        "Source": "https://github.com/airbytehq/airbyte",
        "Tracker": "https://github.com/airbytehq/airbyte/issues",
    },
    packages=find_packages(exclude=("unit_tests", "integration_tests", "docs")),
    package_data={"octavia_cli.generate": ["templates/*.j2"], "octavia_cli.init.example_files": ["example_api_http_headers.yaml"]},
    install_requires=[
        "click~=8.0.3",
        f"airbyte_api_client @ file://{os.getcwd()}/build/airbyte_api_client",
        "jinja2~=3.0.3",
        "deepdiff~=5.7.0",
        "pyyaml~=6.0",
        "analytics-python~=1.4.0",
        "python-slugify~=6.1.2",
    ],
    python_requires=">=3.9.11",
    extras_require={
        "tests": ["MyPy~=0.812", "pytest~=6.2.5", "pytest-cov", "pytest-mock", "pytest-recording", "requests-mock", "pre-commit"],
        "sphinx-docs": [
            "Sphinx~=4.2",
            "sphinx-rtd-theme~=1.0",
        ],
    },
    entry_points={"console_scripts": ["octavia=octavia_cli.entrypoint:octavia"]},
)
