import multiprocessing as mp
import traceback
from typing import Any, List

import dill


def run_in_external_process(fn, timeout: int, max_timeout: int, logger, args:List[Any]) -> Any:
    """
    fn passed in must return a tuple of (desired return value, Exception OR None)
    This allows propagating any errors from the process up and raising accordingly
    """
    result = None
    while result is None:
        q_worker = mp.Queue()
        proc = mp.Process(
            target=multiprocess_queuer,
            # use dill to pickle the function for Windows-compatibility
            args=(dill.dumps(fn), q_worker, *args),
        )
        proc.start()
        try:
            # this attempts to get return value from function with our specified timeout up to max
            result, potential_error = q_worker.get(timeout=min(timeout, max_timeout))
        except mp.queues.Empty:
            if timeout >= max_timeout:  # if we've got to max_timeout and tried once with that value
                raise TimeoutError(
                    f"Timed out too many times while running {fn.__name__}, max timeout of {max_timeout} seconds reached."
                )
            logger.info(f"timed out while running {fn.__name__} after {timeout} seconds, retrying...")
            timeout *= 2  # double timeout and try again
        else:
            if potential_error is None:
                return result
            traceback.print_exception(type(potential_error), potential_error, potential_error.__traceback__)
            raise potential_error
        finally:
            try:
                proc.terminate()
            except Exception as e:
                logger.info(f"'{fn.__name__}' proc unterminated, error: {e}")


def multiprocess_queuer(func, queue: mp.Queue, *args, **kwargs):
    """ this is our multiprocesser helper function, lives at top-level to be Windows-compatible """
    queue.put(dill.loads(func)(*args, **kwargs))
