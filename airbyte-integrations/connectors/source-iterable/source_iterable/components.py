#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

import requests
from requests.exceptions import ChunkedEncodingError

from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor

logger = logging.getLogger("airbyte")


@dataclass
class FaultTolerantJsonlExtractor(DpathExtractor):
    """
    A fault-tolerant JSONL extractor that handles ChunkedEncodingError and malformed JSON gracefully.
    This is needed for large exports from Iterable API that may have connection issues or malformed records.
    Overrides extract_records to handle JSONL decoding with error handling.
    """

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        """
        Extract records from JSONL response line by line, handling errors gracefully.
        Skips malformed lines and continues processing instead of crashing.
        Uses dpath to apply field_path filtering if specified.
        """
        skipped_count = 0
        line_num = 0
        last_line = None
        last_successful_line = None
        last_successful_record = None

        try:
            for line_num, line in enumerate(response.iter_lines(decode_unicode=True), start=1):
                # Skip empty lines
                if not line or not line.strip():
                    continue

                last_line = line  # Keep track of the last line we tried to process

                try:
                    record = json.loads(line)
                    last_successful_line = line  # Update last successful line
                    last_successful_record = record  # Keep track of the last successful record structure
                    # Apply field_path filtering using parent class logic
                    if self.field_path:
                        import dpath.util
                        extracted = dpath.util.get(record, self.field_path, default=[])
                        if isinstance(extracted, list):
                            for item in extracted:
                                yield item
                        elif extracted:
                            yield extracted
                    else:
                        yield record
                except (json.JSONDecodeError, ValueError) as e:
                    skipped_count += 1
                    line_preview = line[:100] if isinstance(line, str) else str(line)[:100]
                    logger.warning(
                        f"Skipping malformed JSON on line {line_num}: {str(e)[:200]}. "
                        f"Line content (first 100 chars): {line_preview}"
                    )
                    continue
        except ChunkedEncodingError as e:
            # Connection was closed prematurely - this can happen with very large responses
            # IMPORTANT: We've already yielded records successfully. Re-raising would cause Airbyte
            # to retry and lose all those records. Instead, we log an error and continue - the
            # incremental sync will resume from the last cursor position.
            records_processed = max(0, line_num - skipped_count - 1)
            logger.error(
                f"Response ended prematurely (ChunkedEncodingError) at line {line_num}. "
                f"Successfully processed {records_processed} records, skipped {skipped_count} malformed records. "
                f"The sync will continue with other date range slices. "
                f"Consider reducing 'incremental_sync_step' config value (e.g., to P7D or P14D) "
                f"to get smaller responses that are less likely to timeout. "
                f"Error: {str(e)}"
            )
            # Don't re-raise - we've already yielded records successfully
            # Re-raising would cause Airbyte to retry and lose all processed records
            # The incremental sync cursor will be updated to the last successful record,
            # so the next sync will automatically resume from where this one left off
        except Exception as e:
            # Catch any other unexpected errors during decoding
            logger.error(
                f"Unexpected error during JSONL extraction at line {line_num}: {type(e).__name__}: {str(e)}"
            )
            raise

        if skipped_count > 0:
            logger.warning(f"Skipped {skipped_count} malformed record(s) during JSONL extraction")


@dataclass
class EventsRecordExtractor(DpathExtractor):
    common_fields = ("itblInternal", "_type", "createdAt", "email")

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        jsonl_records = super().extract_records(response=response)
        for record_dict in jsonl_records:
            record_dict_common_fields = {}
            for field in self.common_fields:
                record_dict_common_fields[field] = record_dict.pop(field, None)
            yield {**record_dict_common_fields, "data": record_dict}
