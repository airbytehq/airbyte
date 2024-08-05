# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import os
import subprocess
import sys
from typing import TYPE_CHECKING
from snoop import logger
from concurrent import futures
import threading
import datetime

if TYPE_CHECKING:
    from typing import IO, Any, Callable, List


def get_connector_command(entrypoint_args: List[str]) -> List[str]:
    return os.environ["AIRBYTE_ENTRYPOINT"].split(" ") + entrypoint_args

class CommandRunner:
    def __init__(self, command: List[str], callback: Callable):
        self.command = command
        self.callback = callback
        self.callback_futures = []
    
    def handle_output(self, process, tee):
        callback_futures = []
        with futures.ThreadPoolExecutor() as callback_executor:
            for line in iter(process.readline, b''):
                seen_at = int(datetime.datetime.now().timestamp() * 1000)
                tee(line)
                future = callback_executor.submit(self.callback, line, seen_at)
                callback_futures.append(future)
        futures.wait(callback_futures, return_when=futures.ALL_COMPLETED)
            
        process.close()   
    
    def run_callback(self, line: Any):
        self.callback(line.decode())

    def run(self) -> int:
        
        logger.info(f"Running {self.command}")
        
        process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        threading.Thread(target=self.handle_output, args=(process.stdout, sys.stdout.buffer.write)).start()
        threading.Thread(target=self.handle_output, args=(process.stderr, sys.stderr.buffer.write)).start()
        
        exit_code = process.wait()
        logger.info(f"Command {self.command} finished with exit code {exit_code}")
        return exit_code
    


# def consume_std(input_io: IO, output_io: TextIO | Any, callback: Callable, tee: bool):
#     with input_io:
#         for line in iter(input_io.readline, ""):
#             if tee:
#                 output_io.write(line)
#             callback(line)
#             input_io.flush()


# def run_command_and_stream_output(command: List[str], callback: Callable, tee: bool) -> Tuple[int, List[str]]:
#     logger.info(f"Running {command}")
#     process = subprocess.Popen(
#         command,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True,
#         bufsize=1,
#         env=os.environ.copy(),
#         cwd="/airbyte/integration_code"
#     )

#     # TODO: use threads if we want to consume both stderr and stdout at the same time
#     consume_std(process.stdout, sys.stdout, callback, tee)
#     consume_std(process.stderr, sys.stderr, callback, tee)

#     return_code = process.wait()

#     return return_code
