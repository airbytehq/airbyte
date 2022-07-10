#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import tempfile
from typing import Any, BinaryIO, Callable, Iterator, Mapping, Optional, TextIO, Tuple, Union

import pyarrow as pa
from pyarrow import json as pa_json
from source_s3.utils import run_in_external_process

from .abstract_file_parser import AbstractFileParser
from .json_spec import JsonFormat

MAX_CHUNK_SIZE = 50.0 * 1024**2  # in bytes
TMP_FOLDER = tempfile.mkdtemp()


class JsonParser(AbstractFileParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.format_model = None

    @property
    def is_binary(self) -> bool:
        return True

    @property
    def format(self) -> JsonFormat:
        if self.format_model is None:
            self.format_model = JsonFormat.parse_obj(self._format)
        return self.format_model

    def _read_options(self) -> Mapping[str, str]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.csv.ReadOptions.html
        build ReadOptions object like: pa.csv.ReadOptions(**self._read_options())
        """
        return {**{"block_size": self.format.block_size, "use_threads": True}}

    def _parse_options(self) -> Mapping[str, str]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.json.ParseOptions.html
         build ParseOptions object like: pa.json.ParseOptions(**self._parse_options())
        """

        return {"newlines_in_values": self.format.newlines_in_values, "unexpected_field_behavior": self.format.unexpected_field_behavior}

    def get_inferred_schema(self, file: Union[TextIO, BinaryIO]) -> Mapping[str, Any]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.json.read_json.html
        This now uses multiprocessing in order to timeout the schema inference as it can hang.
        Since the hanging code is resistant to signal interrupts, threading/futures doesn't help so needed to multiprocess.
        https://issues.apache.org/jira/browse/ARROW-11853?page=com.atlassian.jira.plugin.system.issuetabpanels%3Aall-tabpanel
        """

        def infer_schema_process(file_sample: str, read_opts: dict, parse_opts: dict) -> Tuple[dict, Optional[Exception]]:
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
                    streaming_reader = pa.json.read_json(fp, pa.json.ReadOptions(**read_opts), pa.json.ParseOptions(**parse_opts))
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
        self.logger.debug("inferring schema")
        file_sample = file.read(self._read_options()["block_size"] * 2)  # type: ignore[arg-type]
        return run_in_external_process(
            fn=infer_schema_process,
            timeout=4,
            max_timeout=60,
            logger=self.logger,
            args=[file_sample, self._read_options(), self._parse_options()],
        )

    def stream_records(self, file: Union[TextIO, BinaryIO]) -> Iterator[Mapping[str, Any]]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.json.read_json.html

        """
        json_reader = pa_json.read_json(file, pa.json.ReadOptions(**self._read_options()), pa.json.ParseOptions(**self._parse_options()))
        batch_dict = json_reader.to_pydict()
        batch_columns = [col_info.name for col_info in json_reader.schema]
        # this gives us a list of lists where each nested list holds ordered values for a single column
        # e.g. [ [1,2,3], ["a", "b", "c"], [True, True, False] ]
        columnwise_record_values = [batch_dict[column] for column in batch_columns]
        # we zip this to get row-by-row, e.g. [ [1, "a", True], [2, "b", True], [3, "c", False] ]
        for record_values in zip(*columnwise_record_values):
            # create our record of {col: value, col: value} by dict comprehension, iterating through all cols in batch_columns
            yield {batch_columns[i]: record_values[i] for i in range(len(batch_columns))}
