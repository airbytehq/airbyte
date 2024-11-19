# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import os
import subprocess
import sys
from typing import TYPE_CHECKING

from connectors_canary_testing import logger

if TYPE_CHECKING:
    from typing import IO, Any, Callable, List, TextIO, Tuple


def consume_std(input_io: IO, output_io: TextIO | Any, callback: Callable, tee: bool):
    with input_io:
        for line in iter(input_io.readline, ""):
            if tee:
                output_io.write(line)
            callback(line)
            input_io.flush()


def run_command_and_stream_output(command: List[str], callback: Callable, tee: bool) -> Tuple[int, List[str]]:
    logger.info(f"Running {command}")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=os.environ.copy(),
        cwd="/airbyte/integration_code"
    )

    # TODO: use threads if we want to consume both stderr and stdout at the same time
    consume_std(process.stdout, sys.stdout, callback, tee)
    consume_std(process.stderr, sys.stderr, callback, tee)

    return_code = process.wait()

    return return_code
