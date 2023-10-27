#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk>=0.51.17",
    "smart_open[azure]",
    "pytz",
    "fastavro==1.4.11",
    "pyarrow",
    "unstructured==0.10.19",
    "pdf2image==1.16.3",
    "pdfminer.six==20221105",
    "unstructured[docx]==0.10.19",
    "unstructured.pytesseract>=0.3.12",
    "pytesseract==0.3.10",
    "markdown",
]

TEST_REQUIREMENTS = ["requests-mock~=1.9.3", "pytest-mock~=3.6.1", "pytest~=6.2"]

setup(
    name="source_azure_blob_storage",
    description="Source implementation for Azure Blob Storage.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
