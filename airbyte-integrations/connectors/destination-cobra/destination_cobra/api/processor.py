# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import csv
import logging
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
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


class JobStatus(Enum):
    UPLOADED = "UPLOADED"
    INGESTING = "INGESTING"
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"

    def is_terminal(self):
        return self in {JobStatus.COMPLETE, JobStatus.INCOMPLETE}


@dataclass
class Job:
    id: str
    status: JobStatus


class JobRepository:
    _TERMINAL_STATES = {"Aborted", "Failed", "JobComplete"}
    _FAILED_STATES = {"Aborted", "Failed"}

    def __init__(
        self,
        http_client: HttpClient,
        url_base: str,
        source_to_destination_operation_mapping: Mapping[str, Operation],
        salesforce_assembler: Optional[SalesforceRecordAssembler] = None,
    ) -> None:
        self._http_client = http_client
        self._url_base = url_base
        self._source_to_destination_operation_mapping = source_to_destination_operation_mapping
        self._assembler = salesforce_assembler if salesforce_assembler else SalesforceRecordAssembler(http_client, url_base)

    def create(self, stream: str, batch: Batch) -> Job:
        job_id = self._create_job(stream)
        self._upload_batch(stream, batch, job_id)
        return Job(id=job_id, status=JobStatus.UPLOADED)

    def _create_job(self, stream: str) -> str:
        """
        Returns the ID of the created job.
        """
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
        )

        if create_response.status_code != 200:
            # until we learn more about the different types of error, we will just flag everything as a system error and break the sync
            raise AirbyteTracedException(
                message=f"Unexpected error while pushing a creating a new job: {create_response.content}",
                failure_type=FailureType.system_error,
            )

        job_id = create_response.json()["id"]
        _LOGGER.info(f"Job {job_id} has been created for stream {stream}")
        return job_id

    def _upload_batch(self, stream: str, batch: Batch, job_id: str):
        _, batch_response = self._http_client.send_request(
            http_method="PUT",
            headers={"Content-Type": "text/csv"},
            url=f"{self._url_base}/services/data/v62.0/jobs/ingest/{job_id}/batches",
            data=self._assemble(self._source_to_destination_operation_mapping[stream].sf_object, batch),
            request_kwargs={},
        )
        if batch_response.status_code != 201:
            # until we learn more about the different types of error, we will just flag everything as a system error and break the sync
            raise AirbyteTracedException(
                message=f"Unexpected error while pushing a new batch: {batch_response.content}", failure_type=FailureType.system_error
            )
        else:
            _LOGGER.debug(f"Batch has been created to job {job_id} for stream {stream}")

    def _assemble(self, sf_object: str, batch: Batch) -> str:
        keys = JobRepository._extract_keys(batch)

        string_io = StringIO()
        writer = csv.DictWriter(string_io, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(map(lambda record: self._assembler.assemble(sf_object, record.data), batch.get()))
        return string_io.getvalue()

    @staticmethod
    def _extract_keys(batch: Batch) -> List[str]:
        keys = set()
        for batch_entry in batch.get():
            keys |= set(batch_entry.data.keys())
        return JobRepository._sort(keys)

    @staticmethod
    def _sort(keys: Iterable[str]) -> List[str]:
        """
        This is NOT needed in order to integrate with salesforce but our mock server testing framework lacks the capabilities of matching CSV hence we order the keys here to have consistent results across multiple test executions.
        """
        sorted_keys = list(keys)
        sorted_keys.sort()
        return sorted_keys

    def start_ingestion(self, job: Job, stream: str):
        """
        This method will start the ingestion and update the status of the job.

        Param stream is only used for logging purposed in order for when there will be an error, it is easier to debug and we understand
        how to handle it.
        """
        _, processing_response = self._http_client.send_request(
            http_method="PATCH",
            url=f"{self._url_base}/services/data/v62.0/jobs/ingest/{job.id}",
            json={"state": "UploadComplete"},
            request_kwargs={},
        )
        if processing_response.status_code != 200:
            # until we learn more about the different types of error, we will just flag everything as a system error and break the sync
            raise AirbyteTracedException(
                message=f"Unexpected error while starting job ingestion for stream {stream} on job {job.id}: {processing_response.content}",
                failure_type=FailureType.system_error,
            )
        job.status = JobStatus.INGESTING

    def update_status(self, job: Job, stream: str) -> None:
        _, polling_response = self._http_client.send_request(
            http_method="GET",
            url=f"{self._url_base}/services/data/v62.0/jobs/ingest/{job.id}",
            request_kwargs={},
        )

        job_state = polling_response.json()["state"]
        if job_state in self._TERMINAL_STATES:
            if job_state in self._FAILED_STATES:
                job.status = JobStatus.INCOMPLETE
                _LOGGER.warning(f"Job {job.id} for stream {stream} has failed: {polling_response.content.decode()}")
            else:
                job.status = JobStatus.COMPLETE


class RecordProcessor:
    """
    This class currently assumes that there are no limitations regarding jobs, although we assume there are limits like the number of concurrent jobs.
    """

    _SLEEP_TIMEDELTA = timedelta(seconds=5)

    def __init__(
        self,
        http_client: HttpClient,
        url_base: str,
        source_to_destination_operation_mapping: Mapping[str, Operation],
        max_batch_size_in_bytes: int,
        streams_order: List[str] = None,
        salesforce_assembler: Optional[SalesforceRecordAssembler] = None,
        print_record_content_on_error: bool = False,
    ) -> None:
        self._job_repository = JobRepository(
            http_client,
            url_base,
            source_to_destination_operation_mapping,
            salesforce_assembler if salesforce_assembler else SalesforceRecordAssembler(http_client, url_base),
        )
        self._http_client = http_client
        self._url_base = url_base
        self._source_to_destination_operation_mapping = source_to_destination_operation_mapping
        self._streams_order = streams_order if streams_order else None

        self._jobs_by_stream = defaultdict(list)
        self._max_batch_size_in_bytes = max_batch_size_in_bytes
        self._batch_by_stream = defaultdict(lambda: self._create_batch())
        self._failed_response_parser = GzipParser(CsvParser())
        self._print_record_content_on_error = print_record_content_on_error

    def process(self, record: AirbyteRecordMessage) -> None:
        if record.stream not in self._source_to_destination_operation_mapping:
            raise ValueError(f"Input stream {record.stream} does not have a mapping to a Salesforce object.")

        batch = self._batch_by_stream[record.stream]
        if batch.is_full():
            _LOGGER.debug(f"Batch for stream {record.stream} is full. Sending the batch to Salesforce...")
            self._add_batch(record.stream, batch)

            self._batch_by_stream[record.stream] = self._create_batch()
            self._batch_by_stream[record.stream].add(record)
        else:
            batch.add(record)

    def flush(self) -> None:
        _LOGGER.debug("Flushing...")

        for streams in self._get_streams_processing_order():
            self._flush_streams(streams)

    def _flush_streams(self, streams: Iterable[str]) -> None:
        _LOGGER.debug(f"Processing the batches for streams {streams}...")

        duplicate_sf_objects = [
            sf_object
            for sf_object, count in Counter(self._source_to_destination_operation_mapping[stream].sf_object for stream in streams).items()
            if count > 1
        ]
        if duplicate_sf_objects:
            # There is another solution which is to add more complexity to our code to handle that. For now, I think it is fair to push this on the users side and we can consider this a UX improvement
            _LOGGER.warning(
                f"Multiple streams are trying to write to the same Salesforce objects: {duplicate_sf_objects}. This can cause `UNABLE_TO_LOCK_ROW` errors if they are accessing the same objects. If you are seeing this error, we recommend setting up multiple connections or enable serial mode for Bulk API in Salesforce."
            )

        for stream in streams:
            _LOGGER.debug(f"Creating jobs for batches that weren't full for stream {stream}...")
            self._add_batch(stream, self._batch_by_stream[stream])

        while True:
            _LOGGER.debug(f"Starting new jobs if possible...")
            for stream in streams:
                self._start_next_job_ingestion(stream)

            if all(job.status.is_terminal() for stream in streams for job in self._jobs_by_stream[stream]):
                break
            else:
                time.sleep(self._SLEEP_TIMEDELTA.total_seconds())

        if any(job.status == JobStatus.INCOMPLETE for stream in streams for job in self._jobs_by_stream[stream]):
            # TODO as of today, this return way to handle error does not allow for progressing the state in incremental syncs. Until we figure this out, it'll be all or nothing.
            raise AirbyteTracedException(
                message="This sync was a partial success because some records were skipped", failure_type=FailureType.config_error
            )

    def _start_next_job_ingestion(self, stream: str) -> None:
        jobs_currently_ingesting = self._get_jobs_with_status([stream], JobStatus.INGESTING)
        if jobs_currently_ingesting:
            # update the status to make sure it is still ingesting
            self._update_ingesting_job_statuses(stream)

        jobs_currently_ingesting = self._get_jobs_with_status([stream], JobStatus.INGESTING)
        if not jobs_currently_ingesting:
            jobs_waiting_for_ingestion = self._get_jobs_with_status([stream], JobStatus.UPLOADED)
            if jobs_waiting_for_ingestion:
                self._job_repository.start_ingestion(jobs_waiting_for_ingestion[0], stream)
        else:
            _LOGGER.debug(f"A job is already ingesting for stream {stream} hence we will wait before scheduling a new one")

    def _update_ingesting_job_statuses(self, stream: str) -> None:
        """
        return: True is no failed results in job, else False
        """
        for job in filter(lambda job: job.status == JobStatus.INGESTING, self._jobs_by_stream[stream]):
            self._job_repository.update_status(job, stream)
            if job.status.is_terminal():
                job_has_failed = self._log_failures(job.id)
                if job_has_failed:
                    job.status = JobStatus.INCOMPLETE

            if job.status == JobStatus.COMPLETE:
                _LOGGER.info(f"Job {job.id} successful")

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
        if batch.is_empty():
            # We expect this to happen only if the number of records matches the batch size exactly
            _LOGGER.info(f"Batch for stream {stream} is empty hence a job will not be created")
            return

        job = self._job_repository.create(stream, batch)
        self._jobs_by_stream[stream].append(job)

        if stream in self._get_streams_processing_order()[0]:
            # When adding a batch, we only want to start the ingestion of the job if the streams are the first in the sequence.
            # Potential improvement: if we receive a stream_status "COMPLETE" for the first stream in the sequence, we should be ok to ingest on the second stream of the sequence.
            # Note that hopefully, we will have sequence implemented in the platform so we can clean all sequence related code in the destinations.
            self._start_next_job_ingestion(stream)

    def _get_streams_processing_order(self) -> List[Iterable[str]]:
        if self._streams_order:
            return [[stream] for stream in self._streams_order]
        else:
            return [self._batch_by_stream.keys()]

    def _create_batch(self) -> Batch:
        return Batch(self._max_batch_size_in_bytes)

    def _get_jobs_with_status(self, streams: Iterable[str], status: JobStatus) -> List[Job]:
        return [job for stream in streams for job in self._jobs_by_stream[stream] if job.status == status]
