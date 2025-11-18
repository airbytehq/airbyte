# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import csv
import io
import json
import logging
from dataclasses import InitVar, dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterable, Mapping

import pandas as pd
import pyarrow.parquet as pq
import requests

from airbyte_cdk.sources.declarative.decoders.decoder import Decoder


@dataclass  # Use the dataclass decorator
class FlexibleDecoder(Decoder):
    """
    A custom decoder that dynamically selects the appropriate underlying decoder
    (JSONL, CSV, or Parquet) based on the 'Content-Type' header of the HTTP response.
    CSV parsing options are hardcoded within this class.
    This version assumes files are NOT gzipped.
    """

    parameters: InitVar[Mapping[str, Any]] = None  # Capture any other parameters from manifest

    # CSV parsing options are hardcoded as class attributes or set in __post_init__
    _csv_delimiter: str = ","
    _csv_quote_char: str = '"'
    _csv_encoding: str = "utf-8"
    _csv_skip_rows_before_header: int = 0

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.logger = logging.getLogger("airbyte")
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)
        pass

    def _convert_all_to_strings(self, obj: Any) -> Any:
        """
        Recursively converts all non-None values in a dictionary or list to strings.
        This handles Decimal, datetime.date, datetime.datetime, and other types.
        """
        if obj is None:
            return None
        elif isinstance(obj, (Decimal, datetime, date)):
            return str(obj)  # Convert Decimal, datetime, date to string
        elif isinstance(obj, dict):
            return {k: self._convert_all_to_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_all_to_strings(elem) for elem in obj]
        # For other primitive types (int, float, bool, string already), convert to string
        # This ensures consistency, even if it means converting a string to a string.
        # This is the safest approach for dynamic schemaless sources to Parquet.
        return str(obj)

    def decode(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        """
        Decodes the raw response body from the requests.Response object based on its Content-Type header.

        Args:
            response (requests.Response): The HTTP response object from the request.

        Returns:
            Iterable[Mapping[str, Any]]: An iterable of decoded records (dictionaries).
        """
        content_type = response.headers.get("Content-Type", "").lower()
        content_bytes = response.content

        self.logger.debug(f"CONTENT TYPE: {content_type}")

        if (
            "application/json" in content_type
            or "application/x-jsonlines" in content_type
            or "application/x-jsonl+json" in content_type
            or "application/jsonl" in content_type
        ):
            for line in content_bytes.decode("utf-8").splitlines():
                if line.strip():
                    try:
                        record_dict = json.loads(line)
                        # Convert all values within the record to strings
                        processed_record = self._convert_all_to_strings(record_dict)
                        # Yield the entire processed record as a JSON string under a single key
                        yield {"raw_data": json.dumps(processed_record)}
                    except json.JSONDecodeError as e:
                        logging.warning(f"Skipping malformed JSONL line: {line.strip()} - Error: {e}")
        elif "text/csv" in content_type or "application/csv" in content_type:
            logging.debug("INSIDE CSV DECODER")
            try:
                df = pd.read_csv(
                    io.BytesIO(content_bytes),
                    delimiter=self._csv_delimiter,
                    quotechar=self._csv_quote_char,
                    skiprows=self._csv_skip_rows_before_header,
                    encoding=self._csv_encoding,
                )
                for record_dict in df.to_dict(orient="records"):
                    # Convert all values within the record to strings
                    processed_record = self._convert_all_to_strings(record_dict)
                    # Yield the entire processed record as a JSON string under a single key
                    yield {"raw_data": json.dumps(processed_record)}
            except Exception as e:
                logging.error(f"Error decoding CSV (Content-Type: {content_type}): {e}")
                raise
        elif (
            "application/parquet" in content_type
            or "application/x-parquet" in content_type
            or "application/vnd.apache.parquet" in content_type
            or "application/octet-stream" in content_type
        ):
            self.logger.debug("INSIDE PARQUET DECODER")
            try:
                table = pq.read_table(io.BytesIO(content_bytes))
                df = table.to_pandas()
                for record in df.to_dict(orient="records"):
                    # Convert all values within the record to strings
                    processed_record = self._convert_all_to_strings(record)
                    self.logger.debug(f"Parquet Decoded Record: {record}")
                    # Yield the entire processed record as a JSON string under a single key
                    yield {"raw_data": json.dumps(processed_record)}
            except Exception as e:
                self.logger.error(f"Error decoding Parquet (Content-Type: {content_type}): {e}")
                raise
        else:
            self.logger.error(f"Unsupported or unrecognized Content-Type: {content_type}. Cannot decode response.")
            raise ValueError(f"Unsupported or unrecognized Content-Type: {content_type}")
