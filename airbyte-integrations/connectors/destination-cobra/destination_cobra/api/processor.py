# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import csv
import logging
import time
from collections import defaultdict
from datetime import timedelta
from io import StringIO
from typing import Iterable, List, Mapping, Optional

from airbyte_protocol_dataclasses.models import AirbyteRecordMessage

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.sources.declarative.decoders import GzipParser
from airbyte_cdk.sources.declarative.decoders.composite_raw_decoder import CsvParser
from airbyte_cdk.sources.streams.http import HttpClient
from destination_cobra.api.assembler import SalesforceRecordAssembler
from destination_cobra.processor.batch import Batch


_LOGGER = logging.getLogger("airbyte.api.processor")


class Operation:
    def __init__(self, sf_object: str, operation: str, external_id: Optional[str] = None) -> None:
        self._sf_object = sf_object
        self._operation = operation
        self._external_id = external_id

    @property
    def sf_object(self) -> str:
        return self._sf_object

    @property
    def operation(self) -> str:
        return self._operation

    @property
    def external_id(self) -> Optional[str]:
        return self._external_id


class RecordProcessor:
    """
    This class currently assumes that there are no limitations regarding jobs, although we assume there are limits like the number of concurrent jobs.
    """

    _SLEEP_TIMEDELTA = timedelta(seconds=5)
    _TERMINAL_STATES = {"Aborted", "Failed", "JobComplete"}

    def __init__(
        self,
        http_client: HttpClient,
        url_base: str,
        source_to_destination_operation_mapping: Mapping[str, Operation],
        streams_order: List[str] = None,
        salesforce_assembler: Optional[SalesforceRecordAssembler] = None,
        print_record_content_on_error: bool = False,
    ) -> None:
        self._http_client = http_client
        self._url_base = url_base
        self._source_to_destination_operation_mapping = source_to_destination_operation_mapping
        self._assembler = salesforce_assembler if salesforce_assembler else SalesforceRecordAssembler(http_client, url_base)
        self._streams_order = streams_order if streams_order else None

        self._job_id_by_stream = {}
        self._batches_by_stream = defaultdict(Batch)
        self._failed_response_parser = GzipParser(CsvParser())
        self._print_record_content_on_error = print_record_content_on_error

    def process(self, record: AirbyteRecordMessage) -> None:
        if record.stream not in self._source_to_destination_operation_mapping:
            raise ValueError(f"Input stream {record.stream} does not have a mapping to a Salesforce object.")

        batch = self._batches_by_stream[record.stream]
        if batch.is_full():
            _LOGGER.debug(f"Batch for stream {record.stream} is full. Sending the batch to Salesforce...")
            self._add_batch(record.stream, batch)

            self._batches_by_stream[record.stream] = Batch()
            self._batches_by_stream[record.stream].add(record)
        else:
            batch.add(record)

    def flush(self) -> None:
        _LOGGER.debug("Flushing...")

        for streams in self._get_streams_processing_order():
            self._flush_streams(streams)

    def _flush_streams(self, streams: Iterable[str]) -> None:
        _LOGGER.debug(f"Processing the batches for streams {streams}...")
        for stream in streams:
            self._add_batch(stream, self._batches_by_stream[stream])

        _LOGGER.debug("Mark batches upload as complete...")
        for stream in streams:
            job_id = self._job_id_by_stream[stream]
            _, processing_response = self._http_client.send_request(
                http_method="PATCH",
                url=f"{self._url_base}/services/data/v62.0/jobs/ingest/{job_id}",
                json={"state": "UploadComplete"},
                request_kwargs={},
            )

            if processing_response.status_code != 200:
                # until we learn more about the different types of error, we will just flag everything as a system error and break the sync
                raise AirbyteTracedException(
                    message=f"Unexpected error while starting job ingestion for stream {stream} on job {job_id}: {processing_response.content}",
                    failure_type=FailureType.system_error,
                )

        all_jobs_successful = self._poll_until_job_completion(streams)
        if not all_jobs_successful:
            # TODO as of today, this return way to handle error does not allow for progressing the state in incremental syncs. Until we figure this out, it'll be all or nothing.
            raise AirbyteTracedException(
                message="This sync was a partial success because some records were skipped ", failure_type=FailureType.config_error
            )

    def _poll_until_job_completion(self, streams: Iterable[str]) -> bool:
        """
        return: True is no failed results in job, else False
        """
        has_failure = False
        while True:
            completed_job_ids = []

            _LOGGER.debug(f"Polling for jobs {self._job_id_by_stream.values()}...")
            for stream in streams:
                job_id = self._job_id_by_stream[stream]
                _, polling_response = self._http_client.send_request(
                    http_method="GET",
                    url=f"{self._url_base}/services/data/v62.0/jobs/ingest/{job_id}",
                    request_kwargs={},
                )

                if polling_response.json()["state"] in self._TERMINAL_STATES:
                    completed_job_ids.append(job_id)

                    has_failure = has_failure | self._log_failures(job_id)

                    if polling_response.json()["state"] == "JobComplete":
                        _LOGGER.info(f"Job {job_id} successful")
                    else:
                        _LOGGER.warning(f"Job {job_id} for stream {stream} has failed: {polling_response.content.decode()}")
                        # TODO confirm what should happen in the case where
                        has_failure = True

            self._job_id_by_stream = {
                stream: job_id for stream, job_id in self._job_id_by_stream.items() if job_id not in completed_job_ids
            }
            if self._job_id_by_stream:
                time.sleep(self._SLEEP_TIMEDELTA.total_seconds())
            else:
                break

        return not has_failure

    def _log_failures(self, job_id: str) -> bool:
        has_failure = False

        # Note regarding pagination: we assume there is none because other Bulk API endpoints that do clearly reference a `locator` while https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/get_job_failed_results.htm does not
        _, failed_results_response = self._http_client.send_request(
            http_method="GET",
            url=f"{self._url_base}/services/data/v62.0/jobs/ingest/{job_id}/failedResults",
            request_kwargs={"stream": True},
        )
        for entry in self._failed_response_parser.parse(failed_results_response.raw):
            has_failure = True
            record = (
                {key: value for key, value in entry.items() if key not in {"sf__Id", "sf__Error"}}
                if self._print_record_content_on_error
                else "<obfuscated>"
            )
            if self._failure_has_object_id(entry):
                _LOGGER.warning(
                    f"Salesforce record {entry['sf__Id']} could not be updated:\n\tRecord:{record}\n\tError:{entry['sf__Error']}"
                )
            else:
                _LOGGER.warning(f"Salesforce record could not be inserted:\n\tRecord:{record}\n\tError:{entry['sf__Error']}")
        return has_failure

    def _failure_has_object_id(self, entry):
        return "sf__Id" in entry and entry["sf__Id"]

    def _add_batch(self, stream: str, batch: Batch) -> None:
        if stream not in self._job_id_by_stream:
            self._create_job(stream)

        _, batch_response = self._http_client.send_request(
            http_method="PUT",
            headers={"Content-Type": "text/csv"},
            url=f"{self._url_base}/services/data/v62.0/jobs/ingest/{self._job_id_by_stream[stream]}/batches",
            data=self._assemble(self._source_to_destination_operation_mapping[stream].sf_object, batch),
            request_kwargs={},
        )

        if batch_response.status_code != 201:
            # until we learn more about the different types of error, we will just flag everything as a system error and break the sync
            raise AirbyteTracedException(
                message=f"Unexpected error while pushing a new batch: {batch_response.content}", failure_type=FailureType.system_error
            )
        else:
            _LOGGER.info(f"Batch has been created for stream {stream}")

    def _create_job(self, stream: str) -> None:
        sf_object = self._source_to_destination_operation_mapping[stream].sf_object
        operation = self._source_to_destination_operation_mapping[stream].operation.lower()

        request_body = {"object": sf_object, "operation": operation}
        if operation == "upsert":
            request_body["externalIdFieldName"] = self._source_to_destination_operation_mapping[stream].external_id

        _, create_response = self._http_client.send_request(
            http_method="POST",
            url=f"{self._url_base}/services/data/v62.0/jobs/ingest",
            json=request_body,
            request_kwargs={},
        )  # status is 200

        if create_response.status_code != 200:
            # until we learn more about the different types of error, we will just flag everything as a system error and break the sync
            raise AirbyteTracedException(
                message=f"Unexpected error while pushing a creating a new job: {create_response.content}",
                failure_type=FailureType.system_error,
            )
        else:
            self._job_id_by_stream[stream] = create_response.json()["id"]
            _LOGGER.info(f"Job {self._job_id_by_stream[stream]} has been created for stream {stream}")

    def _get_streams_processing_order(self) -> List[Iterable[str]]:
        if self._streams_order:
            return [[stream] for stream in self._streams_order]
        else:
            return [self._batches_by_stream.keys()]

    def _assemble(self, sf_object: str, batch: Batch) -> str:
        keys = RecordProcessor._extract_keys(batch)

        string_io = StringIO()
        writer = csv.DictWriter(string_io, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(map(lambda record: self._assembler.assemble(sf_object, record.data), batch.get()))
        return string_io.getvalue()

    @staticmethod
    def _extract_keys(batch: Batch) -> List[str]:
        keys = set()
        for object in batch.get():
            keys |= set(object.data.keys())
        return RecordProcessor._sort(keys)

    @staticmethod
    def _sort(keys: Iterable[str]) -> List[str]:
        """
        This is NOT needed in order to integrate with salesforce but our mock server testing framework lacks the capabilities of matching CSV hence we order the keys here to have consistent results across multiple test executions.
        """
        sorted_keys = list(keys)
        sorted_keys.sort()
        return sorted_keys
