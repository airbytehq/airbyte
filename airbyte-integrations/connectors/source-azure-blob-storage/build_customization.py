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
    is large and takes some time to download. It runs a python script that downloads
    the data following connector installation.

    The data is cached to the images /root/nltk_data directory.
    """

    nltk_python_script = textwrap.dedent(
        """
        import nltk

        # inline the index url to make the build reproduceable by pinning the exact version of the nltk packages that are downloaded
        downloader = nltk.downloader.Downloader(server_index_url="data:text/xml;charset=utf-8,%3C%3Fxml%20version%3D%221.0%22%3F%3E%0D%0A%3C%3Fxml-stylesheet%20href%3D%22index.xsl%22%20type%3D%22text%2Fxsl%22%3F%3E%0D%0A%3Cnltk_data%3E%0D%0A%20%20%3Cpackages%3E%0D%0A%20%20%20%20%3Cpackage%20id%3D%22punkt%22%20name%3D%22Punkt%20Tokenizer%20Models%22%20author%3D%22Jan%20Strunk%22%20languages%3D%22Czech%2C%20Danish%2C%20Dutch%2C%20English%2C%20Estonian%2C%20Finnish%2C%20French%2C%20German%2C%20Greek%2C%20Italian%2C%20Malayalam%2C%20Norwegian%2C%20Polish%2C%20Portuguese%2C%20Russian%2C%20Slovene%2C%20Spanish%2C%20Swedish%2C%20Turkish%22%20unzip%3D%221%22%20unzipped_size%3D%2237245719%22%20size%3D%2213905355%22%20checksum%3D%228dd1d8760a0976f96e5c262decd75165%22%20subdir%3D%22tokenizers%22%20url%3D%22https%3A%2F%2Fgithub.com%2Fnltk%2Fnltk_data%2Fraw%2F5db857e6f7df11eabb5e5665836db9ec8df07e28%2Fpackages%2Ftokenizers%2Fpunkt.zip%22%20%2F%3E%0D%0A%20%20%20%20%3Cpackage%20id%3D%22averaged_perceptron_tagger%22%20name%3D%22Averaged%20Perceptron%20Tagger%22%20languages%3D%22English%22%20unzip%3D%221%22%20unzipped_size%3D%226138625%22%20size%3D%222526731%22%20checksum%3D%2205c91d607ee1043181233365b3f76978%22%20subdir%3D%22taggers%22%20url%3D%22https%3A%2F%2Fgithub.com%2Fnltk%2Fnltk_data%2Fraw%2F5db857e6f7df11eabb5e5665836db9ec8df07e28%2Fpackages%2Ftaggers%2Faveraged_perceptron_tagger.zip%22%20%2F%3E%0D%0A%20%20%3C%2Fpackages%3E%0D%0A%20%20%3Ccollections%3E%0D%0A%20%20%3C%2Fcollections%3E%0D%0A%3C%2Fnltk_data%3E")
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
        ["sh", "-c", "apt-get update && apt-get install -y tesseract-ocr=5.3.0-2 poppler-utils=22.12.0-2+b1"], skip_entrypoint=True
    )

    return connector_container

async def pre_connector_install(connector_container: Container) -> Container:
    """
    Handles pre-installation setup for the connector by installing necessary system dependencies such as Tesseract-OCR and Poppler-utils.

    These steps are necessary if the unstructured parser from the file based CDK is exposed in the connector.
    """

    # Install Tesseract and Poppler
    connector_container = install_tesseract_and_poppler(connector_container)

    return connector_container


async def post_connector_install(connector_container: Container) -> Container:
    """
    Handles post-installation setup for the connector by setting up nltk.

    These steps are necessary if the unstructured parser from the file based CDK is exposed in the connector.
    """

    # Setup nltk in the container
    connector_container = setup_nltk(connector_container)

    return connector_container
