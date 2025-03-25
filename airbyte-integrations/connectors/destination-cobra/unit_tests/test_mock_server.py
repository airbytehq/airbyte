# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import gzip
import json
import logging
from io import StringIO
from typing import Any, List, Mapping
from unittest import TestCase
from unittest.mock import Mock, patch

import orjson
import pytest
from destination_cobra import DestinationCobra
from unit_tests.describe_api_response import SalesforceDescribeResponseBuilder, SalesforceFieldBuilder

from airbyte_cdk import AirbyteMessage, AirbyteRecordMessage, AirbyteTracedException, DefaultBackoffException, FailureType, Status, Type
from airbyte_cdk.models import AirbyteMessageSerializer
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_ANY_CATALOG = None
_ANY_RECORD = {"record_id": "any_record_id"}
_CLIENT_ID = "a_client_id"
_CLIENT_SECRET = "a_client_secret"
_ACCESS_TOKEN = "a_access_token"
_REFRESH_TOKEN = "a_refresh_token"
_INSTANCE_URL = "https://instance_url.com"
_INPUT_STREAM = "input_stream"
_ANOTHER_INPUT_STREAM = "another_input_stream"
_SALESFORCE_OBJECT = "salesforce_object"
_A_JOB_ID = "a_job_id"
_A_RECORD_ID = "a_record_id"
_ANOTHER_RECORD_ID = "another_record_id"


class ConfigBuilder:
    def __init__(self):
        self._config = {
            "client_id": "default_client_id",
            "client_secret": "default_client_secret",
            "refresh_token": "default_refresh_token",
            "is_sandbox": False,
            "stream_mappings": [
                {
                    "source_stream": "dummy_mapping_source_stream",
                    "destination_table": "dummy_mapping_destination_table",
                    "update_mode": "UPDATE",
                }
            ],
        }

    def with_client_id(self, client_id: str) -> "ConfigBuilder":
        self._config["client_id"] = client_id
        return self

    def with_client_secret(self, client_secret: str) -> "ConfigBuilder":
        self._config["client_secret"] = client_secret
        return self

    def with_refresh_token(self, refresh_token: str) -> "ConfigBuilder":
        self._config["refresh_token"] = refresh_token
        return self

    def with_is_sandbox(self, is_sandbox: bool) -> "ConfigBuilder":
        self._config["is_sandbox"] = is_sandbox
        return self

    def with_stream_mapping(self, source_stream: str, destination_table: str, update_mode: str) -> "ConfigBuilder":
        self._config["stream_mappings"].append(
            {
                "source_stream": source_stream,
                "destination_table": destination_table,
                "update_mode": update_mode,
            }
        )
        return self

    def with_stream_order(self, order: List[str]) -> "ConfigBuilder":
        self._config["stream_order"] = order
        return self

    def with_print_record_content_on_error(self, print_record_content_on_error: bool) -> "ConfigBuilde":
        self._config["print_record_content_on_error"] = print_record_content_on_error
        return self

    def build(self):
        return self._config


class DestinationCobraTest(TestCase):
    _DUMMY_CONFIG_ARGUMENTS = ["--config", "config.json"]  # those are not needed because we are using the values passed during __init__

    def setUp(self):
        self._logger = Mock(spec=logging.Logger)

    def _destination(self, config: Mapping[str, Any]) -> DestinationCobra:
        return DestinationCobra.create(config, self._logger)

    def _config(self) -> ConfigBuilder:
        return ConfigBuilder().with_client_id(_CLIENT_ID).with_client_secret(_CLIENT_SECRET).with_refresh_token(_REFRESH_TOKEN)

    def _extract_messages(self, stdout: StringIO) -> list[AirbyteMessage]:
        output = stdout.getvalue().strip()
        return [AirbyteMessageSerializer.load(orjson.loads(message)) for message in output.split("\n")]

    @patch("sys.stdout", new_callable=StringIO)
    def test_spec(self, stdout) -> None:
        DestinationCobra.for_spec(self._logger).run(["spec"])

        messages = self._extract_messages(stdout)
        assert len(messages) == 1
        assert messages[0].type == Type.SPEC

    @HttpMocker()
    def test_given_auth_fail_when_check_then_return_connection_status_failed(self, http_mocker) -> None:
        config = self._config().build()
        http_mocker.post(self._authentication_request(config), HttpResponse(json.dumps({"error": "an error"}), 401))

        connection_status = self._destination(config).check(self._logger, config)

        assert connection_status.status == Status.FAILED
        assert "Failed to authenticate" in connection_status.message

    @HttpMocker()
    def test_given_valid_auth_when_check_then_return_connection_status_succeeded(self, http_mocker) -> None:
        config = self._config().build()
        self._given_authentication(http_mocker, config, _INSTANCE_URL, _ACCESS_TOKEN)
        http_mocker.get(
            HttpRequest(f"{_INSTANCE_URL}/services/data/v62.0/sobjects/Contact/describe/"),
            HttpResponse(json.dumps({"response": "any response"}), 200),
        )

        connection_status = self._destination(config).check(self._logger, config)

        assert connection_status.status == Status.SUCCEEDED

    @patch("time.sleep", return_value=None)
    @HttpMocker()
    def test_given_insert_operation_and_record_with_id_when_write_then_complete_successfully(self, sleep, http_mocker) -> None:
        config = self._config().with_stream_mapping(_INPUT_STREAM, _SALESFORCE_OBJECT, "INSERT").build()
        self._given_authentication(http_mocker, config, _INSTANCE_URL, _ACCESS_TOKEN)
        self._mock_salesforce_describe(
            http_mocker,
            _SALESFORCE_OBJECT,
            [SalesforceFieldBuilder().with_name("Id").with_type("id"), SalesforceFieldBuilder().with_name("field_to_be_updated")],
        )

        record_data = {"Id": _A_RECORD_ID, "field_to_be_updated": "new data"}
        self._given_successful_jobs(http_mocker, "insert", f"Id,field_to_be_updated\n{_A_RECORD_ID},new data\n")
        self._mock_failed_results(http_mocker, _A_JOB_ID, '"sf__Id","sf__Error",Id,field_to_be_updated')

        output = list(
            self._destination(config).write(
                config,
                _ANY_CATALOG,
                [AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=_INPUT_STREAM, data=record_data, emitted_at=0))],
            )
        )

        # HttpMocker validates that all expected requests were made
        assert len(output) == 1
        assert output[0].log.message == "Sync completed"

    @patch("time.sleep", return_value=None)
    @HttpMocker()
    def test_given_no_stream_order_and_second_job_error_when_write_then_first_job_does_not_complete(self, sleep, http_mocker) -> None:
        config = (
            self._config()
            .with_stream_mapping(_INPUT_STREAM, _SALESFORCE_OBJECT, "INSERT")
            .with_stream_mapping(_ANOTHER_INPUT_STREAM, _SALESFORCE_OBJECT, "UPDATE")
            .build()
        )
        self._given_authentication(http_mocker, config, _INSTANCE_URL, _ACCESS_TOKEN)

        # successful job

        self._mock_salesforce_describe(
            http_mocker,
            _SALESFORCE_OBJECT,
            [SalesforceFieldBuilder().with_name("Id").with_type("id"), SalesforceFieldBuilder().with_name("field_to_be_updated")],
        )
        self._mock_job_creation(http_mocker, "insert", _A_JOB_ID)
        record_data = {"Id": _A_RECORD_ID, "field_to_be_updated": "new data"}
        self._mock_batch_upload(http_mocker, _A_JOB_ID, f"Id,field_to_be_updated\n{_A_RECORD_ID},new data\n")

        # failed job
        http_mocker.post(
            DestinationCobraTest._job_creation_http_request("update"),
            HttpResponse(
                json.dumps(
                    [
                        {
                            "message": "This is not a known error, just something to fail the sync",
                            "errorCode": "UNEXPECTED_ERROR",  #
                        }
                    ]
                ),
                500,
            ),
        )

        with pytest.raises(DefaultBackoffException) as exception:
            list(
                self._destination(config).write(
                    config,
                    _ANY_CATALOG,
                    [
                        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=_INPUT_STREAM, data=record_data, emitted_at=0)),
                        AirbyteMessage(
                            type=Type.RECORD, record=AirbyteRecordMessage(stream=_ANOTHER_INPUT_STREAM, data=_ANY_RECORD, emitted_at=0)
                        ),
                    ],
                )
            )

        # HttpMocker validates that all expected requests were made

    @patch("time.sleep", return_value=None)
    @HttpMocker()
    def test_given_stream_order_and_second_job_error_when_write_then_complete_first_job(self, sleep, http_mocker) -> None:
        """
        The only way to ensure that a job is fully completed is to fail the second job for an unknown error and ensure that the first job is completed.
        """
        config = (
            self._config()
            .with_stream_mapping(_INPUT_STREAM, _SALESFORCE_OBJECT, "INSERT")
            .with_stream_mapping(_ANOTHER_INPUT_STREAM, _SALESFORCE_OBJECT, "UPDATE")
            .with_stream_order([_INPUT_STREAM, _ANOTHER_INPUT_STREAM])
            .build()
        )
        self._given_authentication(http_mocker, config, _INSTANCE_URL, _ACCESS_TOKEN)
        self._mock_salesforce_describe(
            http_mocker,
            _SALESFORCE_OBJECT,
            [SalesforceFieldBuilder().with_name("Id").with_type("id"), SalesforceFieldBuilder().with_name("field_to_be_updated")],
        )

        # successful job
        record_data = {"Id": _A_RECORD_ID, "field_to_be_updated": "new data"}
        self._given_successful_jobs(http_mocker, "insert", f"Id,field_to_be_updated\n{_A_RECORD_ID},new data\n")
        self._mock_failed_results(http_mocker, _A_JOB_ID, '"sf__Id","sf__Error",Id,field_to_be_updated')

        # failed job
        http_mocker.post(
            DestinationCobraTest._job_creation_http_request("update"),
            HttpResponse(
                json.dumps(
                    [
                        {
                            "message": "This is not a known error, just something to fail the sync",
                            "errorCode": "UNEXPECTED_ERROR",  #
                        }
                    ]
                ),
                500,
            ),
        )

        with pytest.raises(DefaultBackoffException):
            list(
                self._destination(config).write(
                    config,
                    _ANY_CATALOG,
                    [
                        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=_INPUT_STREAM, data=record_data, emitted_at=0)),
                        AirbyteMessage(
                            type=Type.RECORD, record=AirbyteRecordMessage(stream=_ANOTHER_INPUT_STREAM, data=record_data, emitted_at=0)
                        ),
                    ],
                )
            )

        # HttpMocker validates that all expected requests were made

    @patch("time.sleep", return_value=None)
    @HttpMocker()
    def test_given_field_needs_transformation_when_write_then_transformation_is_applied(self, sleep, http_mocker) -> None:
        """
        This test uses datetime transformation to assume that the transformations are wired up properly. More specific tests should be done as unit tests.
        """
        config = self._config().with_stream_mapping(_INPUT_STREAM, _SALESFORCE_OBJECT, "INSERT").build()
        self._given_authentication(http_mocker, config, _INSTANCE_URL, _ACCESS_TOKEN)
        self._mock_salesforce_describe(
            http_mocker,
            _SALESFORCE_OBJECT,
            [
                SalesforceFieldBuilder().with_name("Id").with_type("id"),
                SalesforceFieldBuilder().with_name("date_field").with_type("date"),
                SalesforceFieldBuilder().with_name("datetime_field").with_type("datetime"),
            ],
        )

        record_data = {"Id": _A_RECORD_ID, "datetime_field": "2024-01-01 21:12:21 UTC"}
        self._given_successful_jobs(http_mocker, "insert", f"Id,datetime_field\n{_A_RECORD_ID},2024-01-01T21:12:21.000+00:00\n")
        self._mock_failed_results(http_mocker, _A_JOB_ID, '"sf__Id","sf__Error",Id,datetime_field')

        output = list(
            self._destination(config).write(
                config,
                _ANY_CATALOG,
                [AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=_INPUT_STREAM, data=record_data, emitted_at=0))],
            )
        )

        # HttpMocker validates that all expected requests were made
        assert output[0].log.message == "Sync completed"

    @patch("time.sleep", return_value=None)
    @HttpMocker()
    def test_given_update_operation_and_record_with_id_when_write_then_complete_successfully(self, sleep, http_mocker) -> None:
        config = self._config().with_stream_mapping(_INPUT_STREAM, _SALESFORCE_OBJECT, "UPDATE").build()
        self._given_authentication(http_mocker, config, _INSTANCE_URL, _ACCESS_TOKEN)
        self._mock_salesforce_describe(
            http_mocker,
            _SALESFORCE_OBJECT,
            [SalesforceFieldBuilder().with_name("Id").with_type("id"), SalesforceFieldBuilder().with_name("field_to_be_updated")],
        )

        record_data = {"Id": _A_RECORD_ID, "field_to_be_updated": "new data"}
        self._given_successful_jobs(http_mocker, "update", f"Id,field_to_be_updated\n{_A_RECORD_ID},new data\n")
        self._mock_failed_results(http_mocker, _A_JOB_ID, '"sf__Id","sf__Error",Id,field_to_be_updated')

        output = list(
            self._destination(config).write(
                config,
                _ANY_CATALOG,
                [AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=_INPUT_STREAM, data=record_data, emitted_at=0))],
            )
        )

        # HttpMocker validates that all expected requests were made
        assert len(output) == 1
        assert output[0].log.message == "Sync completed"

    @patch("time.sleep", return_value=None)
    @HttpMocker()
    def test_given_delete_operation_and_record_with_id_when_write_then_complete_successfully(self, sleep, http_mocker) -> None:
        config = self._config().with_stream_mapping(_INPUT_STREAM, _SALESFORCE_OBJECT, "DELETE").build()
        self._given_authentication(http_mocker, config, _INSTANCE_URL, _ACCESS_TOKEN)
        self._mock_salesforce_describe(
            http_mocker,
            _SALESFORCE_OBJECT,
            [SalesforceFieldBuilder().with_name("Id").with_type("id")],
        )

        record_data = {"Id": _A_RECORD_ID}
        self._given_successful_jobs(http_mocker, "delete", f"Id\n{_A_RECORD_ID}\n")
        self._mock_failed_results(http_mocker, _A_JOB_ID, '"sf__Id","sf__Error",Id')

        output = list(
            self._destination(config).write(
                config,
                _ANY_CATALOG,
                [AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=_INPUT_STREAM, data=record_data, emitted_at=0))],
            )
        )

        # HttpMocker validates that all expected requests were made
        assert len(output) == 1
        assert output[0].log.message == "Sync completed"

    @patch("time.sleep", return_value=None)
    @HttpMocker()
    def test_given_error_while_processing_when_write_then_continue_processing_records(self, sleep, http_mocker) -> None:
        operation = "update"
        config = (
            self._config()
            .with_stream_mapping(_INPUT_STREAM, _SALESFORCE_OBJECT, "UPDATE")
            .with_print_record_content_on_error(False)
            .build()
        )
        self._given_authentication(http_mocker, config, _INSTANCE_URL, _ACCESS_TOKEN)
        self._mock_salesforce_describe(
            http_mocker,
            _SALESFORCE_OBJECT,
            [SalesforceFieldBuilder().with_name("Id").with_type("id"), SalesforceFieldBuilder().with_name("field_to_be_updated")],
        )

        data_to_be_updated = {"field_to_be_updated": "new data"}
        a_record = {"Id": _A_RECORD_ID} | data_to_be_updated
        another_record = {"Id": _ANOTHER_RECORD_ID} | data_to_be_updated

        self._mock_job_creation(http_mocker, operation, _A_JOB_ID)
        self._mock_batch_upload(http_mocker, _A_JOB_ID, f"Id,field_to_be_updated\n{_A_RECORD_ID},new data\n{_ANOTHER_RECORD_ID},new data\n")
        self._mock_ingestion_start(http_mocker, _A_JOB_ID)
        self._mock_polling(http_mocker, _A_JOB_ID, ["UploadComplete", "InProgress", "JobComplete"])
        self._mock_failed_results(
            http_mocker, _A_JOB_ID, f'"sf__Id","sf__Error",Id,field_to_be_updated\n,an error from salesforce,{_A_RECORD_ID},new data\n'
        )

        with self.assertLogs("airbyte", level="INFO") as log_capture:
            with pytest.raises(AirbyteTracedException) as exception:
                list(
                    self._destination(config).write(
                        config,
                        _ANY_CATALOG,
                        [
                            AirbyteMessage(
                                type=Type.RECORD, record=AirbyteRecordMessage(stream=_INPUT_STREAM, data=a_record, emitted_at=0)
                            ),
                            AirbyteMessage(
                                type=Type.RECORD, record=AirbyteRecordMessage(stream=_INPUT_STREAM, data=another_record, emitted_at=0)
                            ),
                        ],
                    )
                )

        # HttpMocker validates that all expected requests were made
        assert exception.value.failure_type == FailureType.config_error
        assert "<obfuscated>" in ",".join(log_capture.output)  # checks if the records have been obfuscated

    def _authentication_request(self, config: Mapping[str, Any]) -> HttpRequest:
        return HttpRequest(
            "https://login.salesforce.com/services/oauth2/token",
            body=f"grant_type=refresh_token&client_id={config['client_id']}&client_secret={config['client_secret']}&refresh_token={config['refresh_token']}",
        )

    def _given_authentication(self, http_mocker: HttpMocker, config: Mapping[str, Any], instance_url: str, access_token: str) -> None:
        http_mocker.post(
            self._authentication_request(config),
            HttpResponse(json.dumps({"access_token": access_token, "instance_url": instance_url}), 200),
        )

    def _given_successful_jobs(self, http_mocker: HttpMocker, operation: str, batch_as_csv: str) -> None:
        self._mock_job_creation(http_mocker, operation, _A_JOB_ID)
        self._mock_batch_upload(http_mocker, _A_JOB_ID, batch_as_csv)
        self._mock_ingestion_start(http_mocker, _A_JOB_ID)
        self._mock_polling(http_mocker, _A_JOB_ID, ["UploadComplete", "InProgress", "JobComplete"])

    @staticmethod
    def _mock_job_creation(http_mocker: HttpMocker, operation: str, job_id: str) -> None:
        http_mocker.post(
            DestinationCobraTest._job_creation_http_request(operation),
            HttpResponse(
                json.dumps(
                    {
                        "id": job_id,
                        "operation": operation,
                        "object": _SALESFORCE_OBJECT,
                        "createdById": "0055e000006PQdLAAW",
                        "createdDate": "2025-02-12T22:25:33.000+0000",
                        "systemModstamp": "2025-02-12T22:25:33.000+0000",
                        "state": "Open",
                        "concurrencyMode": "Parallel",
                        "contentType": "CSV",
                        "apiVersion": 62.0,
                        "contentUrl": "services/data/v62.0/jobs/ingest/750cW0000081hKrQAI/batches",
                        "lineEnding": "LF",
                        "columnDelimiter": "COMMA",
                    }
                ),
                200,
            ),
        )

    @staticmethod
    def _job_creation_http_request(operation):
        return HttpRequest(
            f"{_INSTANCE_URL}/services/data/v62.0/jobs/ingest",
            body={"object": _SALESFORCE_OBJECT, "operation": operation},
        )

    @staticmethod
    def _mock_batch_upload(http_mocker: HttpMocker, job_id: str, records_as_csv: str) -> None:
        http_mocker.put(
            HttpRequest(
                f"{_INSTANCE_URL}/services/data/v62.0/jobs/ingest/{job_id}/batches",
                body=records_as_csv,
            ),
            HttpResponse("", 201),
        )

    @staticmethod
    def _mock_ingestion_start(http_mocker: HttpMocker, job_id: str) -> None:
        http_mocker.patch(
            HttpRequest(
                f"{_INSTANCE_URL}/services/data/v62.0/jobs/ingest/{job_id}",
                body={"state": "UploadComplete"},
            ),
            HttpResponse(
                json.dumps(
                    {
                        "id": job_id,
                        "operation": "operation",  # this is not used as of today but it should match the operation provided in the job creation
                        "object": _SALESFORCE_OBJECT,  # this is not used as of today but it should match the operation provided in the job creation
                        "createdById": "0055e000006PQdLAAW",
                        "createdDate": "2025-02-17T14:14:31.000+0000",
                        "systemModstamp": "2025-02-17T14:14:31.000+0000",
                        "state": "UploadComplete",
                        "concurrencyMode": "Parallel",
                        "contentType": "CSV",
                        "apiVersion": 62.0,
                    }
                ),
                200,
            ),
        )

    @staticmethod
    def _mock_polling(http_mocker: HttpMocker, job_id: str, job_statuses: List[str]) -> None:
        http_mocker.get(
            HttpRequest(
                f"{_INSTANCE_URL}/services/data/v62.0/jobs/ingest/{job_id}",
            ),
            [DestinationCobraTest._polling_response(job_id, status) for status in job_statuses],
        )

    @staticmethod
    def _polling_response(job_id: str, job_status: str):
        return HttpResponse(
            json.dumps(
                {
                    "id": job_id,
                    "operation": "operation",  # this is not used as of today but it should match the operation provided in the job creation
                    "object": _SALESFORCE_OBJECT,  # this is not used as of today but it should match the operation provided in the job creation
                    "createdById": "0055e000006PQdLAAW",
                    "createdDate": "2025-02-17T14:08:01.000+0000",
                    "systemModstamp": "2025-02-17T14:09:07.000+0000",
                    "state": job_status,
                    # note that this response was extracted from a "JobCompleted" and other statuses most likely will have different values in the payload
                    "concurrencyMode": "Parallel",
                    "contentType": "CSV",
                    "apiVersion": 62.0,
                    "jobType": "V2Ingest",
                    "lineEnding": "LF",
                    "columnDelimiter": "COMMA",
                    "numberRecordsProcessed": 1,
                    "numberRecordsFailed": 0,
                    "retries": 0,
                    "totalProcessingTime": 7064,
                    "apiActiveProcessingTime": 6926,
                    "apexProcessingTime": 5459,
                    "isPkChunkingSupported": False,
                }
            ),
            200,
        )

    def _mock_failed_results(self, http_mocker: HttpMocker, job_id: str, csv_value: str) -> None:
        http_mocker.get(
            HttpRequest(
                f"{_INSTANCE_URL}/services/data/v62.0/jobs/ingest/{job_id}/failedResults",
            ),
            HttpResponse(self._to_gzip(csv_value), 200),
        )

    def _mock_salesforce_describe(self, http_mocker: HttpMocker, sf_object: str, fields: List[SalesforceFieldBuilder]) -> None:
        response_builder = SalesforceDescribeResponseBuilder(sf_object)
        for field in fields:
            response_builder.with_field(field)

        http_mocker.get(
            HttpRequest(f"{_INSTANCE_URL}/services/data/v62.0/sobjects/{sf_object}/describe/"),
            response_builder.build(),
        )

    @staticmethod
    def _to_gzip(value: str) -> bytes:
        return gzip.compress(bytes(value, "utf-8"))
