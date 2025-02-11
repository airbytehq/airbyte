# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest import TestCase

import pytest

from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_AN_ERROR_RESPONSE = HttpResponse(json.dumps({"errors": ["an error"]}))
_SERVICE_UNAVAILABLE_ERROR_RESPONSE = HttpResponse(json.dumps({"errors": ["Service unavailable"]}), status_code=503)
from freezegun import freeze_time
from requests.exceptions import ConnectionError
from source_shopify import SourceShopify

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.integration.api.authentication import grant_all_scopes, set_up_shop
from unit_tests.integration.api.bulk import (
    JobCreationResponseBuilder,
    JobStatusResponseBuilder,
    MetafieldOrdersJobResponseBuilder,
    create_job_cancel_request,
    create_job_creation_body,
    create_job_creation_request,
    create_job_status_request,
)


_BULK_OPERATION_ID = "gid://shopify/BulkOperation/4472588009661"
_BULK_STREAM = "metafield_orders"
_SHOP_NAME = "airbyte-integration-test"

_JOB_START_DATE = datetime.fromisoformat("2024-05-05T00:00:00+00:00")
_JOB_END_DATE = _JOB_START_DATE + timedelta(hours=2, minutes=24)

_URL_GRAPHQL = f"https://{_SHOP_NAME}.myshopify.com/admin/api/2024-04/graphql.json"
_JOB_RESULT_URL = "https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/bulk-operation-outputs/l6lersgk4i81iqc3n6iisywwtipb-final?GoogleAccessId=assets-us-prod%40shopify-tiers.iam.gserviceaccount.com&Expires=1715633149&Signature=oMjQelfAzUW%2FdulC3HbuBapbUriUJ%2Bc9%2FKpIIf954VTxBqKChJAdoTmWT9ymh%2FnCiHdM%2BeM%2FADz5siAC%2BXtHBWkJfvs%2F0cYpse0ueiQsw6R8gW5JpeSbizyGWcBBWkv5j8GncAnZOUVYDxRIgfxcPb8BlFxBfC3wsx%2F00v9D6EHbPpkIMTbCOAhheJdw9GmVa%2BOMqHGHlmiADM34RDeBPrvSo65f%2FakpV2LBQTEV%2BhDt0ndaREQ0MrpNwhKnc3vZPzA%2BliOGM0wyiYr9qVwByynHq8c%2FaJPPgI5eGEfQcyepgWZTRW5S0DbmBIFxZJLN6Nq6bJ2bIZWrVriUhNGx2g%3D%3D&response-content-disposition=attachment%3B+filename%3D%22bulk-4476008693949.jsonl%22%3B+filename%2A%3DUTF-8%27%27bulk-4476008693949.jsonl&response-content-type=application%2Fjsonl"

_INCREMENTAL_JOB_START_DATE_ISO = "2024-05-05T00:00:00+00:00"
_INCREMENTAL_JOB_START_DATE = datetime.fromisoformat(_INCREMENTAL_JOB_START_DATE_ISO)
_INCREMENTAL_JOB_END_DATE = _INCREMENTAL_JOB_START_DATE + timedelta(hours=24, minutes=0)


def _get_config(start_date: datetime, bulk_window: int = 1, job_checkpoint_interval=200000) -> Dict[str, Any]:
    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "shop": _SHOP_NAME,
        "credentials": {
            "auth_method": "api_password",
            "api_password": "api_password",
        },
        "bulk_window_in_days": bulk_window,
        "job_checkpoint_interval": job_checkpoint_interval,
    }


@freeze_time(_JOB_END_DATE)
class GraphQlBulkStreamTest(TestCase):
    def setUp(self) -> None:
        self._http_mocker = HttpMocker()
        self._http_mocker.__enter__()

        set_up_shop(self._http_mocker, _SHOP_NAME)
        grant_all_scopes(self._http_mocker, _SHOP_NAME)

    def tearDown(self) -> None:
        self._http_mocker.__exit__(None, None, None)

    def test_when_read_then_extract_records(self) -> None:
        self._http_mocker.post(
            create_job_creation_request(_SHOP_NAME, _JOB_START_DATE, _JOB_END_DATE),
            JobCreationResponseBuilder().with_bulk_operation_id(_BULK_OPERATION_ID).build(),
        )
        self._http_mocker.post(
            create_job_status_request(_SHOP_NAME, _BULK_OPERATION_ID),
            JobStatusResponseBuilder().with_completed_status(_BULK_OPERATION_ID, _JOB_RESULT_URL).build(),
        )
        self._http_mocker.get(
            HttpRequest(_JOB_RESULT_URL),
            MetafieldOrdersJobResponseBuilder().with_record().with_record().build(),
        )

        output = self._read(_get_config(_JOB_START_DATE))

        assert output.errors == []
        assert len(output.records) == 2

    def test_given_errors_on_job_creation_when_read_then_do_not_retry(self) -> None:
        """
        The purpose of this test is to document the current behavior as I'm not sure we have an example of such errors on the job creation
        """
        job_creation_request = create_job_creation_request(_SHOP_NAME, _JOB_START_DATE, _JOB_END_DATE)
        self._http_mocker.post(job_creation_request, _AN_ERROR_RESPONSE)

        self._read(_get_config(_JOB_START_DATE))

        self._http_mocker.assert_number_of_calls(job_creation_request, 1)

    def test_given_response_is_not_json_on_job_creation_when_read_then_retry(self) -> None:
        job_creation_request = create_job_creation_request(_SHOP_NAME, _JOB_START_DATE, _JOB_END_DATE)
        self._http_mocker.post(
            job_creation_request,
            [
                HttpResponse("This is not json"),
                JobCreationResponseBuilder()
                .with_bulk_operation_id(_BULK_OPERATION_ID)
                .build(),  # This will never get called (see assertion below)
            ],
        )

        self._http_mocker.post(
            create_job_status_request(_SHOP_NAME, _BULK_OPERATION_ID),
            JobStatusResponseBuilder().with_completed_status(_BULK_OPERATION_ID, _JOB_RESULT_URL).build(),
        )
        self._http_mocker.get(
            HttpRequest(_JOB_RESULT_URL),
            MetafieldOrdersJobResponseBuilder().with_record().with_record().build(),
        )

        output = self._read(_get_config(_JOB_START_DATE))

        assert output.errors == []
        assert len(output.records) == 2

    def test_given_connection_error_on_job_creation_when_read_then_retry_job_creation(self) -> None:
        inner_mocker = self._http_mocker.__getattribute__("_mocker")
        inner_mocker.register_uri(  # TODO the testing library should have the ability to generate ConnectionError. As this might not be trivial, we will wait for another case before implementing
            "POST",
            _URL_GRAPHQL,
            [
                {"exc": ConnectionError("ConnectionError")},
                {"text": JobCreationResponseBuilder().with_bulk_operation_id(_BULK_OPERATION_ID).build().body, "status_code": 200},
            ],
            additional_matcher=lambda request: request.text == create_job_creation_body(_JOB_START_DATE, _JOB_END_DATE),
        )
        self._http_mocker.post(
            create_job_status_request(_SHOP_NAME, _BULK_OPERATION_ID),
            JobStatusResponseBuilder().with_completed_status(_BULK_OPERATION_ID, _JOB_RESULT_URL).build(),
        )
        self._http_mocker.get(
            HttpRequest(_JOB_RESULT_URL),
            MetafieldOrdersJobResponseBuilder().with_record().with_record().build(),
        )

        output = self._read(_get_config(_JOB_START_DATE))

        assert output.errors == []

    def test_given_retryable_error_on_first_get_job_status_when_read_then_retry(self) -> None:
        self._http_mocker.post(
            create_job_creation_request(_SHOP_NAME, _JOB_START_DATE, _JOB_END_DATE),
            JobCreationResponseBuilder().with_bulk_operation_id(_BULK_OPERATION_ID).build(),
        )
        self._http_mocker.post(
            create_job_status_request(_SHOP_NAME, _BULK_OPERATION_ID),
            [
                _AN_ERROR_RESPONSE,
                JobStatusResponseBuilder().with_completed_status(_BULK_OPERATION_ID, _JOB_RESULT_URL).build(),
            ],
        )
        self._http_mocker.get(
            HttpRequest(_JOB_RESULT_URL),
            MetafieldOrdersJobResponseBuilder().with_record().with_record().build(),
        )

        output = self._read(_get_config(_JOB_START_DATE))

        assert output.errors == []
        assert len(output.records) == 2

    def test_given_retryable_error_on_get_job_status_when_read_then_retry(self) -> None:
        self._http_mocker.post(
            create_job_creation_request(_SHOP_NAME, _JOB_START_DATE, _JOB_END_DATE),
            JobCreationResponseBuilder().with_bulk_operation_id(_BULK_OPERATION_ID).build(),
        )
        self._http_mocker.post(
            create_job_status_request(_SHOP_NAME, _BULK_OPERATION_ID),
            [
                JobStatusResponseBuilder().with_running_status(_BULK_OPERATION_ID).build(),
                HttpResponse(json.dumps({"errors": ["an error"]})),
                JobStatusResponseBuilder().with_completed_status(_BULK_OPERATION_ID, _JOB_RESULT_URL).build(),
            ],
        )
        self._http_mocker.get(
            HttpRequest(_JOB_RESULT_URL),
            MetafieldOrdersJobResponseBuilder().with_record().with_record().build(),
        )

        output = self._read(_get_config(_JOB_START_DATE))

        assert output.errors == []
        assert len(output.records) == 2

    def _read(self, config):
        catalog = CatalogBuilder().with_stream(_BULK_STREAM, SyncMode.full_refresh).build()
        output = read(SourceShopify(), config, catalog)
        return output


@freeze_time(_INCREMENTAL_JOB_END_DATE)
class GraphQlBulkStreamIncrementalTest(TestCase):
    def setUp(self) -> None:
        self._http_mocker = HttpMocker()
        self._http_mocker.__enter__()

        set_up_shop(self._http_mocker, _SHOP_NAME)
        grant_all_scopes(self._http_mocker, _SHOP_NAME)

    def tearDown(self) -> None:
        self._http_mocker.__exit__(None, None, None)

    def test_when_read_then_extract_records(self) -> None:
        job_created_at = _INCREMENTAL_JOB_END_DATE - timedelta(minutes=5)
        self._http_mocker.post(
            create_job_creation_request(_SHOP_NAME, _INCREMENTAL_JOB_START_DATE, _INCREMENTAL_JOB_END_DATE),
            JobCreationResponseBuilder(job_created_at=job_created_at.strftime("%Y-%m-%dT%H:%M:%SZ"))
            .with_bulk_operation_id(_BULK_OPERATION_ID)
            .build(),
        )
        self._http_mocker.post(
            create_job_status_request(_SHOP_NAME, _BULK_OPERATION_ID),
            JobStatusResponseBuilder().with_completed_status(_BULK_OPERATION_ID, _JOB_RESULT_URL).build(),
        )
        self._http_mocker.get(
            HttpRequest(_JOB_RESULT_URL),
            MetafieldOrdersJobResponseBuilder().with_record().with_record().build(),
        )
        # expectation is job start date should be the updated_at in orders
        metafield_orders_orders_state = {
            "orders": {"updated_at": _INCREMENTAL_JOB_START_DATE_ISO, "deleted": {"deleted_at": ""}},
            "updated_at": _INCREMENTAL_JOB_START_DATE_ISO,
        }
        stream_state = StateBuilder().with_stream_state(_BULK_STREAM, metafield_orders_orders_state).build()

        # we are passing to config a start date let's set something "old" as happen in many sources like 2 years ago
        config_start_date = _INCREMENTAL_JOB_START_DATE - timedelta(weeks=104)
        output = self._read(_get_config(config_start_date), sync_mode=SyncMode.incremental, state=stream_state)

        assert output.errors == []
        assert len(output.records) == 2

    def test_when_read_with_updated_at_field_before_bulk_request_window_start_date(self) -> None:
        """ "
        The motivation of this test is https://github.com/airbytehq/oncall/issues/6874

        In this scenario we end having stream_slices method to generate same slice N times.
        Our checkpointing logic will trigger when job_checkpoint_interval is passed, but there may be the case that such checkpoint
        has the same value as the current slice start date so we would end requesting same job.

        In this test:
        1. First job requires to checkpoint as we pass the 1500 limit, it cancels the bulk job and checkpoints from last cursor value.
        2. Next job just goes "fine".
        3. Now in the third and N job is where the behavior described above occurs, I just set it to happen a fixed N times as the
        test depends on we keep feeding responses in the order of status running/canceled, but you can observe the repeated slices in the
        logging.

        e.g.

        {"type":"LOG","log":{"level":"INFO","message":"Stream: `metafield_orders` requesting BULK Job for period: 2024-05-02T17:30:00+00:00 -- 2024-05-03T17:30:00+00:00. Slice size: `P1D`. The BULK checkpoint after `15000` lines."}}
        ...
        {"type":"LOG","log":{"level":"INFO","message":"Stream metafield_orders, continue from checkpoint: `2024-05-02T17:30:00+00:00`."}}
        {"type":"LOG","log":{"level":"INFO","message":"Stream: `metafield_orders` requesting BULK Job for period: 2024-05-02T17:30:00+00:00 -- 2024-05-03T17:30:00+00:00. Slice size: `P1D`. The BULK checkpoint after `15000` lines."}}
        {"type":"LOG","log":{"level":"INFO","message":"Stream: `metafield_orders`, the BULK Job: `gid://shopify/BulkOperation/4472588009771` is CREATED"}}
        ...
        """

        def add_n_records(builder, n, record_date: Optional[str] = None):
            for _ in range(n):
                builder = builder.with_record(updated_at=record_date)
            return builder

        # *************** 1st bulk job ***************************
        job_created_at = _INCREMENTAL_JOB_END_DATE - timedelta(minutes=5)
        # create a job request
        self._http_mocker.post(
            create_job_creation_request(_SHOP_NAME, _INCREMENTAL_JOB_START_DATE, _INCREMENTAL_JOB_END_DATE),
            JobCreationResponseBuilder(job_created_at=job_created_at.strftime("%Y-%m-%dT%H:%M:%SZ"))
            .with_bulk_operation_id(_BULK_OPERATION_ID)
            .build(),
        )
        # get job status
        self._http_mocker.post(
            create_job_status_request(_SHOP_NAME, _BULK_OPERATION_ID),
            [
                JobStatusResponseBuilder().with_running_status(_BULK_OPERATION_ID, object_count="500").build(),
                # this should make the job get canceled as it gets over 15000 rows
                JobStatusResponseBuilder().with_running_status(_BULK_OPERATION_ID, object_count="16000").build(),
                # this will complete the job
                JobStatusResponseBuilder().with_canceled_status(_BULK_OPERATION_ID, _JOB_RESULT_URL, object_count="1700").build(),
            ],
        )
        # mock the cancel operation request as we passed the 15000 rows
        self._http_mocker.post(create_job_cancel_request(_SHOP_NAME, _BULK_OPERATION_ID), [HttpResponse(json.dumps({}), status_code=200)])
        # get results for the request that got cancelled
        adjusted_checkpoint_start_date = _INCREMENTAL_JOB_START_DATE - timedelta(days=2, hours=6, minutes=30)
        adjusted_record_date = adjusted_checkpoint_start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        self._http_mocker.get(
            HttpRequest(_JOB_RESULT_URL),
            # MetafieldOrdersJobResponseBuilder().with_record().with_record().build(),
            add_n_records(MetafieldOrdersJobResponseBuilder(), 80, adjusted_record_date).build(),
        )

        # *************** 2nd bulk job ***************************
        # create a job request for a new job with checkpoint date
        # that will be the adjusted_record_date + 1 day
        next_bulk_operation_id = "gid://shopify/BulkOperation/4472588009771"
        adjusted_checkpoint_end_date = adjusted_checkpoint_start_date + timedelta(days=1)
        job_created_at = _INCREMENTAL_JOB_END_DATE - timedelta(minutes=4)
        self._http_mocker.post(
            # The start date is caused by record date in previous iteration
            create_job_creation_request(_SHOP_NAME, adjusted_checkpoint_start_date, adjusted_checkpoint_end_date),
            JobCreationResponseBuilder(job_created_at=job_created_at.strftime("%Y-%m-%dT%H:%M:%SZ"))
            .with_bulk_operation_id(next_bulk_operation_id)
            .build(),
        )
        # get job status
        next_job_result_url = "https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/bulk-operation-outputs/l6lersgk4i81iqc3n6iisywwtipb-final?GoogleAccessId=assets-us-prod%40shopify-tiers.iam.gserviceaccount.com&Expires=1715633149&Signature=oMjQelfAzUW%2FdulC3HbuBapbUriUJ%2Bc9%2FKpIIf954VTxBqKChJAdoTmWT9ymh%2FnCiHdM%2BeM%2FADz5siAC%2BXtHBWkJfvs%2F0cYpse0ueiQsw6R8gW5JpeSbizyGWcBBWkv5j8GncAnZOUVYDxRIgfxcPb8BlFxBfC3wsx%2F00v9D6EHbPpkIMTbCOAhheJdw9GmVa%2BOMqHGHlmiADM34RDeBPrvSo65f%2FakpV2LBQTEV%2BhDt0ndaREQ0MrpNwhKnc3vZPzA%2BliOGM0wyiYr9qVwByynHq8c%2FaJPPgI5eGEfQcyepgWZTRW5S0DbmBIFxZJLN6Nq6bJ2bIZWrVriUhNGx2g%3D%3D&response-content-disposition=attachment%3B+filename%3D%22bulk-4476008693950.jsonl%22%3B+filename%2A%3DUTF-8%27%27bulk-4476008693950.jsonl&response-content-type=application%2Fjsonl"
        self._http_mocker.post(
            create_job_status_request(_SHOP_NAME, next_bulk_operation_id),
            [
                # this will output the job is running
                JobStatusResponseBuilder().with_completed_status(next_bulk_operation_id, next_job_result_url).build(),
            ],
        )
        # get results for the request that got cancelled
        self._http_mocker.get(
            HttpRequest(next_job_result_url),
            # MetafieldOrdersJobResponseBuilder().with_record().with_record().build(),
            add_n_records(MetafieldOrdersJobResponseBuilder(), 90, adjusted_record_date).build(),
        )

        # *************** 3rd and n+ bulk job ***************************
        next_bulk_operation_id = "gid://shopify/BulkOperation/4472588009881"
        adjusted_checkpoint_start_date = adjusted_checkpoint_end_date
        adjusted_checkpoint_end_date = adjusted_checkpoint_start_date + timedelta(days=1)
        job_created_at = _INCREMENTAL_JOB_END_DATE - timedelta(minutes=4)
        create_job_request = create_job_creation_request(_SHOP_NAME, adjusted_checkpoint_start_date, adjusted_checkpoint_end_date)

        self._http_mocker.post(
            create_job_request,
            JobCreationResponseBuilder(job_created_at=job_created_at.strftime("%Y-%m-%dT%H:%M:%SZ"))
            .with_bulk_operation_id(next_bulk_operation_id)
            .build(),
        )

        base_status_responses = [
            JobStatusResponseBuilder().with_running_status(next_bulk_operation_id, object_count="500").build(),
            # this should make the job get canceled as it gets over 15000 rows
            JobStatusResponseBuilder().with_running_status(next_bulk_operation_id, object_count="16000").build(),
            # this will complete the job
            JobStatusResponseBuilder().with_canceled_status(next_bulk_operation_id, next_job_result_url, object_count="1700").build(),
        ]

        n_times_to_loop = 4
        responses_in_loop = base_status_responses * n_times_to_loop
        # get job status
        next_job_result_url = "https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/bulk-operation-outputs/l6lersgk4i81iqc3n6iisywwtipb-final?GoogleAccessId=assets-us-prod%40shopify-tiers.iam.gserviceaccount.com&Expires=1715633149&Signature=oMjQelfAzUW%2FdulC3HbuBapbUriUJ%2Bc9%2FKpIIf954VTxBqKChJAdoTmWT9ymh%2FnCiHdM%2BeM%2FADz5siAC%2BXtHBWkJfvs%2F0cYpse0ueiQsw6R8gW5JpeSbizyGWcBBWkv5j8GncAnZOUVYDxRIgfxcPb8BlFxBfC3wsx%2F00v9D6EHbPpkIMTbCOAhheJdw9GmVa%2BOMqHGHlmiADM34RDeBPrvSo65f%2FakpV2LBQTEV%2BhDt0ndaREQ0MrpNwhKnc3vZPzA%2BliOGM0wyiYr9qVwByynHq8c%2FaJPPgI5eGEfQcyepgWZTRW5S0DbmBIFxZJLN6Nq6bJ2bIZWrVriUhNGx2g%3D%3D&response-content-disposition=attachment%3B+filename%3D%22bulk-4476008693960.jsonl%22%3B+filename%2A%3DUTF-8%27%27bulk-4476008693960.jsonl&response-content-type=application%2Fjsonl"

        self._http_mocker.post(create_job_status_request(_SHOP_NAME, next_bulk_operation_id), responses_in_loop)

        # mock the cancel operation request as we passed the 15000 rows
        self._http_mocker.post(
            create_job_cancel_request(_SHOP_NAME, next_bulk_operation_id), [HttpResponse(json.dumps({}), status_code=200)]
        )

        # get results
        adjusted_record_date = adjusted_checkpoint_start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        self._http_mocker.get(
            HttpRequest(next_job_result_url),
            add_n_records(MetafieldOrdersJobResponseBuilder(), 80, adjusted_record_date).build(),
        )

        # ********* end of request mocking *************

        metafield_orders_orders_state = {
            "orders": {"updated_at": _INCREMENTAL_JOB_START_DATE_ISO, "deleted": {"deleted_at": ""}},
            "updated_at": _INCREMENTAL_JOB_START_DATE_ISO,
        }
        stream_state = StateBuilder().with_stream_state(_BULK_STREAM, metafield_orders_orders_state).build()

        # we are passing to config a start date let's set something "old" as happen in many sources like 2 years ago
        config_start_date = _INCREMENTAL_JOB_START_DATE - timedelta(weeks=104)
        output = self._read(
            _get_config(config_start_date, job_checkpoint_interval=15000), sync_mode=SyncMode.incremental, state=stream_state
        )

        expected_error_message = "The stream: `metafield_orders` checkpoint collision is detected."
        result = output.errors[0].trace.error.internal_message

        # The result of the test should be the `ShopifyBulkExceptions.BulkJobCheckpointCollisionError`
        assert result is not None and expected_error_message in result

    def _read(self, config, sync_mode=SyncMode.full_refresh, state: Optional[List[AirbyteStateMessage]] = None):
        catalog = CatalogBuilder().with_stream(_BULK_STREAM, sync_mode).build()
        output = read(SourceShopify(), config, catalog, state=state)
        return output
