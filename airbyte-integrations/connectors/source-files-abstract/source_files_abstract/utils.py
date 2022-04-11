#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import bz2
import gzip
import linecache
import multiprocessing as mp
import os
import shutil
import traceback
import tracemalloc
from functools import wraps
from multiprocessing import Queue
from typing import Any, Callable, List, Mapping

import dill
from airbyte_cdk.logger import AirbyteLogger


def run_in_external_process(fn: Callable, timeout: int, max_timeout: int, logger: AirbyteLogger, args: List[Any]) -> Mapping[str, Any]:
    """
    fn passed in must return a tuple of (desired return value, Exception OR None)
    This allows propagating any errors from the process up and raising accordingly
    """
    result = None
    while result is None:
        q_worker: Queue = mp.Queue()
        proc = mp.Process(
            target=multiprocess_queuer,
            # use dill to pickle the function for Windows-compatibility
            args=(dill.dumps(fn), q_worker, *args),
        )
        proc.start()
        try:
            # this attempts to get return value from function with our specified timeout up to max
            result, potential_error = q_worker.get(timeout=min(timeout, max_timeout))
        except mp.queues.Empty:  # type: ignore[attr-defined]
            if timeout >= max_timeout:  # if we've got to max_timeout and tried once with that value
                raise TimeoutError(f"Timed out too many times while running {fn.__name__}, max timeout of {max_timeout} seconds reached.")
            logger.info(f"timed out while running {fn.__name__} after {timeout} seconds, retrying...")
            timeout *= 2  # double timeout and try again
        else:
            if potential_error is None:
                return result  # type: ignore[no-any-return]
            traceback.print_exception(type(potential_error), potential_error, potential_error.__traceback__)
            raise potential_error
        finally:
            try:
                proc.terminate()
            except Exception as e:
                logger.info(f"'{fn.__name__}' proc unterminated, error: {e}")


def multiprocess_queuer(func: Callable, queue: mp.Queue, *args: Any, **kwargs: Any) -> None:
    """this is our multiprocesser helper function, lives at top-level to be Windows-compatible"""
    queue.put(dill.loads(func)(*args, **kwargs))


def memory_limit(max_memory_in_megabytes: int, print_limit: int = 20) -> Callable:
    """Runs a test function by a separate process with restricted memory"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: List[Any], **kwargs: Any) -> Any:
            tracemalloc.start()
            result = func(*args, **kwargs)

            # get memory usage immediately after function call, we interested in "first_size" value
            first_size, first_peak = tracemalloc.get_traced_memory()
            # get snapshot immediately just in case we will use it
            snapshot = tracemalloc.take_snapshot()

            # only if we exceeded the quota, build log_messages with traces
            first_size_in_megabytes = first_size / 1024**2
            if first_size_in_megabytes > max_memory_in_megabytes:
                log_messages: List[str] = []
                top_stats = snapshot.statistics("lineno")
                for index, stat in enumerate(top_stats[:print_limit], 1):
                    frame = stat.traceback[0]
                    filename = os.sep.join(frame.filename.split(os.sep)[-2:])
                    log_messages.append("#%s: %s:%s: %.1f KiB" % (index, filename, frame.lineno, stat.size / 1024))
                    line = linecache.getline(frame.filename, frame.lineno).strip()
                    if line:
                        log_messages.append(f"    {line}")
                traceback_log = "\n".join(log_messages)
                assert False, f"Overuse of memory, used: {first_size_in_megabytes}Mb, limit: {max_memory_in_megabytes}Mb!!\n{traceback_log}"

            return result

        return wrapper

    return decorator


def compress(archive_name: str, filename: str) -> str:
    compress_filename = f"{filename}.{archive_name}"
    with open(filename, "rb") as f_in:
        if archive_name == "gz":
            with gzip.open(compress_filename, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        elif archive_name == "bz2":
            with bz2.open(compress_filename, "wb") as f_out:  # type: ignore[assignment]
                shutil.copyfileobj(f_in, f_out)
        else:
            raise NotImplementedError(f"archive type {archive_name} currently unsupported")
    return compress_filename
