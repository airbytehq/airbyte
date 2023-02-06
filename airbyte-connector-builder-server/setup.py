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
    name="connector-builder-server",
    version="0.40.32",
    description="",
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
    keywords="connect-builder",
    project_urls={
        "Documentation": "https://docs.airbyte.io/",
        "Source": "https://github.com/airbytehq/airbyte",
        "Tracker": "https://github.com/airbytehq/airbyte/issues",
    },
    packages=find_packages(exclude=("unit_tests", "integration_tests", "docs")),
    package_data={},
    install_requires=["airbyte-cdk==0.25", "fastapi", "uvicorn"],
    python_requires=">=3.9.11",
    extras_require={
        "tests": [
            "MyPy~=0.812",
            "pytest~=6.2.5",
            "pytest-cov",
            "pytest-mock",
            "pytest-recording",
            "requests-mock",
            "pre-commit",
        ],
    },
)
