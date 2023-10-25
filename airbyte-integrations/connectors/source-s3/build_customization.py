#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dagger import Container


async def post_connector_install(connector_container: Container) -> Container:
    """
    We want to seed the connector with nltk data at build time.
    This is because the nltk data is large and takes a long time to download.
    To do so we run a python script that downloads the data following connector installation.
    """

    nltk_python_script = textwrap.dedent(
        """
        import nltk
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        """
    )
    return (
        connector_container.with_new_file("/tmp/nltk_python_script.py", nltk_python_script)
        .with_exec(["python", "/tmp/nltk_python_script.py"], skip_entrypoint=True)
        .with_exec(["rm", "/tmp/nltk_python_script.py"], skip_entrypoint=True)
    )
