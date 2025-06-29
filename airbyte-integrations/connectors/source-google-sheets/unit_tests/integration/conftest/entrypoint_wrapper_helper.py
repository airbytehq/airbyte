#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import tempfile
from pathlib import Path
from typing import Any, Mapping

from airbyte_cdk.sources import Source
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, _run_command, make_file, read


def check(
    source: Source,
    config: Mapping[str, Any],
    expecting_exception: bool = False,
) -> EntrypointOutput:
    """
    config must be json serializable
    :param expecting_exception: By default if there is an uncaught exception, the exception will be printed out. If this is expected, please
        provide expecting_exception=True so that the test output logs are cleaner
    """

    with tempfile.TemporaryDirectory() as tmp_directory:
        tmp_directory_path = Path(tmp_directory)
        config_file = make_file(tmp_directory_path / "config.json", config)

        return _run_command(source, ["check", "--config", config_file, "--debug"], expecting_exception)
