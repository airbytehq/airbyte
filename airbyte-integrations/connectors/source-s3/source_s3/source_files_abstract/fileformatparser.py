#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import json
import multiprocessing as mp
from abc import ABC, abstractmethod
from typing import Any, BinaryIO, Iterator, Mapping, Optional, TextIO, Tuple, Union

import dill
import pyarrow as pa
from airbyte_cdk.logger import AirbyteLogger
from pyarrow import csv as pa_csv


def multiprocess_queuer(func, queue: mp.Queue, *args, **kwargs):
    """ this is our multiprocesser helper function, lives at top-level to be Windows-compatible """
    queue.put(dill.loads(func)(*args, **kwargs))


class FileFormatParser(ABC):
    def __init__(self, format: dict, master_schema: dict = None):
        """
        :param format: file format specific mapping as described in spec.json
        :param master_schema: superset schema determined from all files, might be unused for some formats, defaults to None
        """
        self._format = format
        self._master_schema = (
            master_schema  # this may need to be used differently by some formats, pyarrow allows extra columns in csv schema
        )
        self.logger = AirbyteLogger()

    @property
    @abstractmethod
    def is_binary(self):
        """
        Override this per format so that file-like objects passed in are currently opened as binary or not
        """

    @abstractmethod
    def get_inferred_schema(self, file: Union[TextIO, BinaryIO]) -> dict:
        """
        Override this with format-specifc logic to infer the schema of file
        Note: needs to return inferred schema with JsonSchema datatypes

        :param file: file-like object (opened via StorageFile)
        :return: mapping of {columns:datatypes} where datatypes are JsonSchema types
        """

    @abstractmethod
    def stream_records(self, file: Union[TextIO, BinaryIO]) -> Iterator[Mapping[str, Any]]:
        """
        Override this with format-specifc logic to stream each data row from the file as a mapping of {columns:values}
        Note: avoid loading the whole file into memory to avoid OOM breakages

        :param file: file-like object (opened via StorageFile)
        :yield: data record as a mapping of {columns:values}
        """

    @staticmethod
    def json_type_to_pyarrow_type(typ: str, reverse: bool = False, logger: AirbyteLogger = AirbyteLogger()) -> str:
        """
        Converts Json Type to PyArrow types to (or the other way around if reverse=True)

        :param typ: Json type if reverse is False, else PyArrow type
        :param reverse: switch to True for PyArrow type -> Json type, defaults to False
        :param logger: defaults to AirbyteLogger()
        :return: PyArrow type if reverse is False, else Json type
        """
        str_typ = str(typ)
        # this is a map of airbyte types to pyarrow types. The first list element of the pyarrow types should be the one to use where required.
        map = {
            "boolean": ("bool_", "bool"),
            "integer": ("int64", "int8", "int16", "int32", "uint8", "uint16", "uint32", "uint64"),
            "number": ("float64", "float16", "float32", "decimal128", "decimal256", "halffloat", "float", "double"),
            "string": ("large_string", "string"),
            "object": ("large_string",),  # TODO: support object type rather than coercing to string
            "array": ("large_string",),  # TODO: support array type rather than coercing to string
            "null": ("large_string",),
        }
        if not reverse:
            for json_type, pyarrow_types in map.items():
                if str_typ.lower() == json_type:
                    return getattr(
                        pa, pyarrow_types[0]
                    ).__call__()  # better way might be necessary when we decide to handle more type complexity
            logger.debug(f"JSON type '{str_typ}' is not mapped, falling back to default conversion to large_string")
            return pa.large_string()
        else:
            for json_type, pyarrow_types in map.items():
                if any([str_typ.startswith(pa_type) for pa_type in pyarrow_types]):
                    return json_type
            logger.debug(f"PyArrow type '{str_typ}' is not mapped, falling back to default conversion to string")
            return "string"  # default type if unspecified in map

    @staticmethod
    def json_schema_to_pyarrow_schema(schema: Mapping[str, Any], reverse: bool = False) -> Mapping[str, Any]:
        """
        Converts a schema with JsonSchema datatypes to one with PyArrow types (or the other way if reverse=True)
        This utilises json_type_to_pyarrow_type() to convert each datatype

        :param schema: json/pyarrow schema to convert
        :param reverse: switch to True for PyArrow schema -> Json schema, defaults to False
        :return: converted schema dict
        """
        new_schema = {}

        for column, json_type in schema.items():
            new_schema[column] = FileFormatParser.json_type_to_pyarrow_type(json_type, reverse=reverse)

        return new_schema


class CsvParser(FileFormatParser):
    @property
    def is_binary(self):
        return True

    def _read_options(self):
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.csv.ReadOptions.html

        build ReadOptions object like: pa.csv.ReadOptions(**self._read_options())
        """
        return {"block_size": self._format.get("block_size", 10000), "encoding": self._format.get("encoding", "utf8")}

    def _parse_options(self):
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.csv.ParseOptions.html

        build ParseOptions object like: pa.csv.ParseOptions(**self._parse_options())
        """
        quote_char = self._format.get("quote_char", False) if self._format.get("quote_char", False) != "" else False
        return {
            "delimiter": self._format.get("delimiter", ","),
            "quote_char": quote_char,
            "double_quote": self._format.get("double_quote", True),
            "escape_char": self._format.get("escape_char", False),
            "newlines_in_values": self._format.get("newlines_in_values", False),
        }

    def _convert_options(self, json_schema: Mapping[str, Any] = None):
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.csv.ConvertOptions.html

        build ConvertOptions object like: pa.csv.ConvertOptions(**self._convert_options())

        :param json_schema: if this is passed in, pyarrow will attempt to enforce this schema on read, defaults to None
        """
        check_utf8 = True if self._format.get("encoding", "utf8").lower().replace("-", "") == "utf8" else False
        convert_schema = self.json_schema_to_pyarrow_schema(json_schema) if json_schema is not None else None
        return {
            **{"check_utf8": check_utf8, "column_types": convert_schema},
            **json.loads(self._format.get("additional_reader_options", "{}")),
        }

    def _run_in_external_process(self, fn, timeout: int, max_timeout: int, *args) -> Any:
        """
        fn passed in must return a tuple of (desired return value, Exception OR None)
        This allows propagating any errors from the process up and raising accordingly

        """
        result = None
        while result is None:
            q_worker = mp.Queue()
            proc = mp.Process(
                target=multiprocess_queuer,
                args=(dill.dumps(fn), q_worker, *args),  # use dill to pickle the function for Windows-compatibility
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
                self.logger.info(f"timed out while running {fn.__name__} after {timeout} seconds, retrying...")
                timeout *= 2  # double timeout and try again
            else:
                if potential_error is not None:
                    raise potential_error
                else:
                    return result
            finally:
                try:
                    proc.terminate()
                except Exception as e:
                    self.logger.info(f"'{fn.__name__}' proc unterminated, error: {e}")

    def get_inferred_schema(self, file: Union[TextIO, BinaryIO]) -> dict:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.csv.open_csv.html

        This now uses multiprocessing in order to timeout the schema inference as it can hang.
        Since the hanging code is resistant to signal interrupts, threading/futures doesn't help so needed to multiprocess.
        https://issues.apache.org/jira/browse/ARROW-11853?page=com.atlassian.jira.plugin.system.issuetabpanels%3Aall-tabpanel
        """

        def infer_schema_process(
            file_sample: str, read_opts: dict, parse_opts: dict, convert_opts: dict
        ) -> Tuple[dict, Optional[Exception]]:
            """
            we need to reimport here to be functional on Windows systems since it doesn't have fork()
            https://docs.python.org/3.7/library/multiprocessing.html#contexts-and-start-methods

            This returns a tuple of (schema_dict, None OR Exception).
            If return[1] is not None and holds an exception we then raise this in the main process.
            This lets us propagate up any errors (that aren't timeouts) and raise correctly.
            """
            try:
                import tempfile

                import pyarrow as pa

                # writing our file_sample to a temporary file to then read in and schema infer as before
                with tempfile.TemporaryFile() as fp:
                    fp.write(file_sample)
                    fp.seek(0)
                    streaming_reader = pa.csv.open_csv(
                        fp, pa.csv.ReadOptions(**read_opts), pa.csv.ParseOptions(**parse_opts), pa.csv.ConvertOptions(**convert_opts)
                    )
                    schema_dict = {field.name: field.type for field in streaming_reader.schema}

            except Exception as e:
                # we pass the traceback up otherwise the main process won't know the exact method+line of error
                return (None, e)
            else:
                return (schema_dict, None)

        # boto3 objects can't be pickled (https://github.com/boto/boto3/issues/678)
        # and so we can't multiprocess with the actual fileobject on Windows systems
        # we're reading block_size*2 bytes here, which we can then pass in and infer schema from block_size bytes
        # the *2 is to give us a buffer as pyarrow figures out where lines actually end so it gets schema correct
        file_sample = file.read(self._read_options()["block_size"] * 2)
        schema_dict = self._run_in_external_process(
            infer_schema_process, 4, 60, file_sample, self._read_options(), self._parse_options(), self._convert_options()
        )
        return self.json_schema_to_pyarrow_schema(schema_dict, reverse=True)

    def stream_records(self, file: Union[TextIO, BinaryIO]) -> Iterator[Mapping[str, Any]]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.csv.open_csv.html
        PyArrow returns lists of values for each column so we zip() these up into records which we then yield
        """
        streaming_reader = pa_csv.open_csv(
            file,
            pa.csv.ReadOptions(**self._read_options()),
            pa.csv.ParseOptions(**self._parse_options()),
            pa.csv.ConvertOptions(**self._convert_options(self._master_schema)),
        )
        still_reading = True
        while still_reading:
            try:
                batch = streaming_reader.read_next_batch()
            except StopIteration:
                still_reading = False
            else:
                batch_dict = batch.to_pydict()
                batch_columns = [col_info.name for col_info in batch.schema]
                # this gives us a list of lists where each nested list holds ordered values for a single column
                # e.g. [ [1,2,3], ["a", "b", "c"], [True, True, False] ]
                columnwise_record_values = [batch_dict[column] for column in batch_columns]
                # we zip this to get row-by-row, e.g. [ [1, "a", True], [2, "b", True], [3, "c", False] ]
                for record_values in zip(*columnwise_record_values):
                    # create our record of {col: value, col: value} by dict comprehension, iterating through all cols in batch_columns
                    yield {batch_columns[i]: record_values[i] for i in range(len(batch_columns))}
