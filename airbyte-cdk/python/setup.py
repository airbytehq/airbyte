#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pathlib

from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

avro_dependency = "avro~=1.11.2"
fastavro_dependency = "fastavro~=1.8.0"
pyarrow_dependency = "pyarrow~=15.0.0"

langchain_dependency = "langchain==0.0.271"
openai_dependency = "openai[embeddings]==0.27.9"
cohere_dependency = "cohere==4.21"
tiktoken_dependency = "tiktoken==0.4.0"

unstructured_dependencies = [
    "unstructured==0.10.27",  # can't be bumped higher due to transitive dependencies we can't provide
    "unstructured[docx,pptx]==0.10.27",
    "pdf2image==1.16.3",
    "pdfminer.six==20221105",
    "unstructured.pytesseract>=0.3.12",
    "pytesseract==0.3.10",
    "markdown",
]

setup(
    name="airbyte-cdk",
    # The version of the airbyte-cdk package is used at runtime to validate manifests. That validation must be
    # updated if our semver format changes such as using release candidate versions.
    version="0.69.2",
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
        "Programming Language :: Python :: 3.8",
    ],
    keywords="airbyte connector-development-kit cdk",
    project_urls={
        "Documentation": "https://docs.airbyte.io/",
        "Source": "https://github.com/airbytehq/airbyte",
        "Tracker": "https://github.com/airbytehq/airbyte/issues",
    },
    packages=find_packages(exclude=("unit_tests",)),
    package_data={"airbyte_cdk": ["py.typed", "sources/declarative/declarative_component_schema.yaml"]},
    install_requires=[
        "airbyte-protocol-models==0.5.1",
        "backoff",
        "dpath~=2.0.1",
        "isodate~=0.6.1",
        "jsonschema~=3.2.0",
        "jsonref~=0.2",
        "pendulum<3.0.0",
        "genson==1.2.2",
        "pydantic>=1.10.8,<2.0.0",
        "pyrate-limiter~=3.1.0",
        "python-dateutil",
        "PyYAML>=6.0.1",
        "requests",
        "requests_cache",
        "Deprecated~=1.2",
        "Jinja2~=3.1.2",
        "cachetools",
        "wcmatch==8.4",
    ],
    python_requires=">=3.8",
    extras_require={
        "dev": [
            avro_dependency,
            fastavro_dependency,
            "freezegun",
            "mypy",
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "requests-mock",
            "pytest-httpserver",
            "pandas==2.0.3",
            pyarrow_dependency,
            langchain_dependency,
            openai_dependency,
            cohere_dependency,
            tiktoken_dependency,
            *unstructured_dependencies,
        ],
        "sphinx-docs": [
            "Sphinx~=4.2",
            "sphinx-rtd-theme~=1.0",
        ],
        "file-based": [
            avro_dependency,
            fastavro_dependency,
            pyarrow_dependency,
            *unstructured_dependencies,
        ],
        "vector-db-based": [langchain_dependency, openai_dependency, cohere_dependency, tiktoken_dependency],
    },
)
