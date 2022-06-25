#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import multiprocessing as mp
import traceback
from multiprocessing import Queue
from typing import Any, Callable, List, Mapping

import dill
import pyarrow as pa


def run_in_external_process(fn: Callable, timeout: int, max_timeout: int, logger: logging.Logger, args: List[Any]) -> Mapping[str, Any]:
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


def get_value_or_json_if_empty_string(options: str) -> str:
    return options.strip() or "{}"


def json_type_to_pyarrow_type(typ: str, logger: logging.Logger, reverse: bool = False) -> str:
    """
    Converts Json Type to PyArrow types to (or the other way around if reverse=True)

    :param typ: Json type if reverse is False, else PyArrow type
    :param logger: Logger object to use for logging
    :param reverse: switch to True for PyArrow type -> Json type, defaults to False
    :return: PyArrow type if reverse is False, else Json type
    """
    str_typ = str(typ)
    # this is a map of airbyte types to pyarrow types. The first list element of the pyarrow types should be the one to use where required.
    map = {
        "boolean": ("bool_", "bool"),
        "integer": ("int64", "int8", "int16", "int32", "uint8", "uint16", "uint32", "uint64"),
        "number": ("float64", "float16", "float32", "decimal128", "decimal256", "halffloat", "float", "double"),
        "string": ("large_string", "string"),
        # TODO: support object type rather than coercing to string
        "object": ("large_string",),
        # TODO: support array type rather than coercing to string
        "array": ("large_string",),
        "null": ("large_string",),
    }
    if not reverse:
        for json_type, pyarrow_types in map.items():
            if str_typ.lower() == json_type:
                return str(
                    getattr(pa, pyarrow_types[0]).__call__()
                )  # better way might be necessary when we decide to handle more type complexity
        logger.debug(f"JSON type '{str_typ}' is not mapped, falling back to default conversion to large_string")
        return str(pa.large_string())
    else:
        for json_type, pyarrow_types in map.items():
            if any(str_typ.startswith(pa_type) for pa_type in pyarrow_types):
                return json_type
        logger.debug(f"PyArrow type '{str_typ}' is not mapped, falling back to default conversion to string")
        return "string"  # default type if unspecified in map


def json_schema_to_pyarrow_schema(schema: Mapping[str, Any], logger: logging.Logger, reverse: bool = False) -> Mapping[str, Any]:
    """
    Converts a schema with JsonSchema datatypes to one with PyArrow types (or the other way if reverse=True)
    This utilises json_type_to_pyarrow_type() to convert each datatype

    :param schema: json/pyarrow schema to convert
    :param reverse: switch to True for PyArrow schema -> Json schema, defaults to False
    :return: converted schema dict
    """
    return {column: json_type_to_pyarrow_type(json_type, logger, reverse=reverse) for column, json_type in schema.items()}
