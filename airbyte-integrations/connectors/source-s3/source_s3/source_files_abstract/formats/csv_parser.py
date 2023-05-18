#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import codecs
import csv
import json
import tempfile
from typing import Any, BinaryIO, Callable, Iterator, Mapping, Optional, TextIO, Tuple, Union

import pyarrow
import pyarrow as pa
import six  # type: ignore[import]
from airbyte_cdk.models import FailureType
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from pyarrow import csv as pa_csv
from pyarrow.lib import ArrowInvalid
from source_s3.exceptions import S3Exception
from source_s3.source_files_abstract.file_info import FileInfo
from source_s3.utils import get_value_or_json_if_empty_string, run_in_external_process

from .abstract_file_parser import AbstractFileParser
from .csv_spec import CsvFormat

MAX_CHUNK_SIZE = 50.0 * 1024**2  # in bytes
TMP_FOLDER = tempfile.mkdtemp()


def wrap_exception(exceptions: Tuple[type, ...]):
    def wrapper(fn: callable):
        def inner(self, file: Union[TextIO, BinaryIO], file_info: FileInfo):
            try:
                return fn(self, file, file_info)
            except exceptions as e:
                raise S3Exception(file_info, str(e), str(e), exception=e)

        return inner

    return wrapper


class CsvParser(AbstractFileParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.format_model = None

    @property
    def is_binary(self) -> bool:
        return True

    @property
    def format(self) -> CsvFormat:
        if self.format_model is None:
            self.format_model = CsvFormat.parse_obj(self._format)
        return self.format_model

    @staticmethod
    def _validate_field(
        format_: Mapping[str, Any], field_name: str, allow_empty: bool = False, disallow_values: Optional[Tuple[Any, ...]] = None
    ) -> Optional[str]:
        disallow_values = disallow_values or ()
        field_value = format_.get(field_name)
        if not field_value and allow_empty:
            return
        if field_value and len(field_value) != 1:
            return f"{field_name} should contain 1 character only"
        if field_value in disallow_values:
            return f"{field_name} can not be {field_value}"

    @classmethod
    def _validate_options(cls, validator: Callable, options_name: str, format_: Mapping[str, Any]) -> Optional[str]:
        options = format_.get(options_name, "{}")
        try:
            options = json.loads(options)
            validator(**options)
        except json.decoder.JSONDecodeError:
            return "Malformed advanced read options!"
        except TypeError as e:
            return f"One or more read options are invalid: {str(e)}"

    @classmethod
    def _validate_read_options(cls, format_: Mapping[str, Any]) -> Optional[str]:
        return cls._validate_options(pa.csv.ReadOptions, "advanced_options", format_)

    @classmethod
    def _validate_convert_options(cls, format_: Mapping[str, Any]) -> Optional[str]:
        return cls._validate_options(pa.csv.ConvertOptions, "additional_reader_options", format_)

    def _validate_config(self, config: Mapping[str, Any]):
        format_ = config.get("format", {})
        for error_message in (
            self._validate_field(format_, "delimiter", disallow_values=("\r", "\n")),
            self._validate_field(format_, "quote_char"),
            self._validate_field(format_, "escape_char", allow_empty=True),
            self._validate_read_options(format_),
            self._validate_convert_options(format_),
        ):
            if error_message:
                raise AirbyteTracedException(error_message, error_message, failure_type=FailureType.config_error)

        try:
            codecs.lookup(format_.get("encoding"))
        except LookupError:
            raise AirbyteTracedException(error_message, error_message, failure_type=FailureType.config_error)

    def _read_options(self) -> Mapping[str, str]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.csv.ReadOptions.html
        build ReadOptions object like: pa.csv.ReadOptions(**self._read_options())
        """
        advanced_options = get_value_or_json_if_empty_string(self.format.advanced_options)
        return {
            **{"block_size": self.format.block_size, "encoding": self.format.encoding},
            **json.loads(advanced_options),
        }

    def _parse_options(self) -> Mapping[str, str]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.csv.ParseOptions.html
        build ParseOptions object like: pa.csv.ParseOptions(**self._parse_options())
        """

        return {
            "delimiter": self.format.delimiter,
            "quote_char": self.format.quote_char,
            "double_quote": self.format.double_quote,
            "escape_char": self.format.escape_char,
            "newlines_in_values": self.format.newlines_in_values,
        }

    def _convert_options(self, json_schema: Mapping[str, Any] = None) -> Mapping[str, Any]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.csv.ConvertOptions.html
        build ConvertOptions object like: pa.csv.ConvertOptions(**self._convert_options())
        :param json_schema: if this is passed in, pyarrow will attempt to enforce this schema on read, defaults to None
        """
        check_utf8 = self.format.encoding.lower().replace("-", "") == "utf8"
        additional_reader_options = get_value_or_json_if_empty_string(self.format.additional_reader_options)
        convert_schema = self.json_schema_to_pyarrow_schema(json_schema) if json_schema is not None else None
        return {
            **{"check_utf8": check_utf8, "column_types": convert_schema},
            **json.loads(additional_reader_options),
        }

    @wrap_exception((ValueError,))
    def get_inferred_schema(self, file: Union[TextIO, BinaryIO], file_info: FileInfo) -> Mapping[str, Any]:
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
                    fp.write(file_sample)  # type: ignore[arg-type]
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
        schema_dict = self._get_schema_dict(file, infer_schema_process)
        return self.json_schema_to_pyarrow_schema(schema_dict, reverse=True)  # type: ignore[no-any-return]

    def _get_schema_dict(self, file: Union[TextIO, BinaryIO], infer_schema_process: Callable) -> Mapping[str, Any]:
        if not self.format.infer_datatypes:
            return self._get_schema_dict_without_inference(file)
        self.logger.debug("inferring schema")
        file_sample = file.read(self._read_options()["block_size"] * 2)  # type: ignore[arg-type]
        return run_in_external_process(
            fn=infer_schema_process,
            timeout=4,
            max_timeout=60,
            logger=self.logger,
            args=[
                file_sample,
                self._read_options(),
                self._parse_options(),
                self._convert_options(),
            ],
        )

    # TODO Rename this here and in `_get_schema_dict`
    def _get_schema_dict_without_inference(self, file: Union[TextIO, BinaryIO]) -> Mapping[str, Any]:
        self.logger.debug("infer_datatypes is False, skipping infer_schema")
        delimiter = self.format.delimiter
        quote_char = self.format.quote_char
        reader = csv.reader([six.ensure_text(file.readline())], delimiter=delimiter, quotechar=quote_char)
        field_names = next(reader)
        file.seek(0)  # the file may be reused later so return the cursor to the very beginning of the file as if nothing happened here
        return {field_name.strip(): pyarrow.string() for field_name in field_names}

    @wrap_exception((ValueError,))
    def stream_records(self, file: Union[TextIO, BinaryIO], file_info: FileInfo) -> Iterator[Mapping[str, Any]]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.csv.open_csv.html
        PyArrow returns lists of values for each column so we zip() these up into records which we then yield
        """
        # In case master_schema is a user defined schema, it may miss some columns.
        # We set their type to `string` as a default type in order to pass a schema with all the file columns to pyarrow
        # so that pyarrow wouldn't need to infer data types of missing columns. Type inference may often break syncs:
        # it reads a block of data and makes suggestions of its type based on that block. So if the next block contains data
        # of different type, things get broken. To fix it you either have to increase block size or pass a predefined schema.
        # Even if actual data type is changed because of this hack, it will not break sync because this data is written
        # to `_ab_additional_properties` column which is not strictly typed ({'type': 'object'}). That's why this is helpful
        # when a schema is defined by user and there's no space to increase a block size.
        schema = self._get_schema_dict_without_inference(file)
        schema.update(self._master_schema)

        streaming_reader = pa_csv.open_csv(
            file,
            pa.csv.ReadOptions(**self._read_options()),
            pa.csv.ParseOptions(**self._parse_options()),
            pa.csv.ConvertOptions(**self._convert_options(schema)),
        )
        still_reading = True
        while still_reading:
            try:
                batch = streaming_reader.read_next_batch()
            except ArrowInvalid as e:
                error_message = "Possibly too small block size used. Please try to increase it"
                raise AirbyteTracedException(message=error_message, failure_type=FailureType.config_error) from e
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

    @classmethod
    def set_minimal_block_size(cls, format: Mapping[str, Any]):
        pass
