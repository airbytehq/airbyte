#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dagger import Container


def setup_nltk(connector_container: Container) -> Container:
    """
    Seeds the connector with nltk data at build time. This is because the nltk data
    is large and takes a long time to download. It runs a python script that downloads
    the data following connector installation.
    """

    nltk_python_script = textwrap.dedent(
        """
        import nltk
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        """
    )
    connector_container = (
        connector_container.with_new_file("/tmp/nltk_python_script.py", nltk_python_script)
        .with_exec(["python", "/tmp/nltk_python_script.py"], skip_entrypoint=True)
        .with_exec(["rm", "/tmp/nltk_python_script.py"], skip_entrypoint=True)
    )

    return connector_container


def install_tesseract_and_poppler(connector_container: Container) -> Container:
    """
    Installs Tesseract-OCR and Poppler-utils in the container. These tools are necessary for
    OCR (Optical Character Recognition) processes and working with PDFs, respectively.
    """

    connector_container = connector_container.with_exec(
        ["sh", "-c", "apt-get update && apt-get install -y tesseract-ocr poppler-utils"], skip_entrypoint=True
    )

    return connector_container


async def post_connector_install(connector_container: Container) -> Container:
    """
    Handles post-installation setup for the connector by setting up nltk and
    installing necessary system dependencies such as Tesseract-OCR and Poppler-utils.
    """

    # Setup nltk in the container
    connector_container = setup_nltk(connector_container)

    # Install Tesseract and Poppler
    connector_container = install_tesseract_and_poppler(connector_container)

    return connector_container
