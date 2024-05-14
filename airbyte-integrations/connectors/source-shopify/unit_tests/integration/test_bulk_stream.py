from datetime import datetime, timedelta
from unittest import TestCase

from source_shopify import SourceShopify
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from freezegun import freeze_time
from airbyte_protocol.models import SyncMode, FailureType
from typing import Any, Dict
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http.request import HttpRequest
from unit_tests.integration.api.authentication import grant_all_scopes, set_up_shop
from unit_tests.integration.api.bulk import JobCreationResponseBuilder, JobStatusResponseBuilder, MetafieldOrdersJobResponseBuilder, create_job_creation_request, create_job_status_request

_BULK_OPERATION_ID = "gid://shopify/BulkOperation/4472588009661"
_BULK_STREAM = "metafield_orders"
_SHOP_NAME = "airbyte-integration-test"

_JOB_START_DATE = datetime.fromisoformat("2024-05-05T00:00:00+00:00")
_JOB_END_DATE = _JOB_START_DATE + timedelta(hours=2, minutes=24)

_URL_GRAPHQL = f"https://{_SHOP_NAME}.myshopify.com/admin/api/2023-07/graphql.json"
_JOB_RESULT_URL = "https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/bulk-operation-outputs/l6lersgk4i81iqc3n6iisywwtipb-final?GoogleAccessId=assets-us-prod%40shopify-tiers.iam.gserviceaccount.com&Expires=1715633149&Signature=oMjQelfAzUW%2FdulC3HbuBapbUriUJ%2Bc9%2FKpIIf954VTxBqKChJAdoTmWT9ymh%2FnCiHdM%2BeM%2FADz5siAC%2BXtHBWkJfvs%2F0cYpse0ueiQsw6R8gW5JpeSbizyGWcBBWkv5j8GncAnZOUVYDxRIgfxcPb8BlFxBfC3wsx%2F00v9D6EHbPpkIMTbCOAhheJdw9GmVa%2BOMqHGHlmiADM34RDeBPrvSo65f%2FakpV2LBQTEV%2BhDt0ndaREQ0MrpNwhKnc3vZPzA%2BliOGM0wyiYr9qVwByynHq8c%2FaJPPgI5eGEfQcyepgWZTRW5S0DbmBIFxZJLN6Nq6bJ2bIZWrVriUhNGx2g%3D%3D&response-content-disposition=attachment%3B+filename%3D%22bulk-4476008693949.jsonl%22%3B+filename%2A%3DUTF-8%27%27bulk-4476008693949.jsonl&response-content-type=application%2Fjsonl"


def _get_config(start_date: datetime, bulk_window: int = 1) -> Dict[str, Any]:
    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "shop": _SHOP_NAME,
        "credentials": {
            "auth_method": "api_password",
            "api_password": "api_password",
        },
        "bulk_window_in_days": bulk_window
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

    def test_given_connection_error_when_read_then_fail_to_sync(self) -> None:
        """
        We want to fix this behavior in a subsequent release so that instead, we retry and have records being emitted
        """
        inner_mocker = self._http_mocker.__getattribute__("_mocker")
        inner_mocker.register_uri(  # TODO the testing library should have the ability to generate ConnectionError. As this might not be trivial, we will wait for another case before implementing
            "POST",
            _URL_GRAPHQL,
            [{"exc": ConnectionError("ConnectionError")}, {"text": JobCreationResponseBuilder().with_bulk_operation_id(_BULK_OPERATION_ID).build().body, "status_code": 200}],
        )

        output = self._read(_get_config(_JOB_START_DATE))

        assert list(map(lambda error: error.trace.error.failure_type, output.errors)) == [FailureType.system_error, FailureType.config_error]  # The actual error followed by the error that crashes the python app
        assert "ConnectionError" in output.errors[0].__str__()

    def _read(self, config):
        catalog = CatalogBuilder().with_stream(_BULK_STREAM, SyncMode.full_refresh).build()
        output = read(SourceShopify(), config, catalog)
        return output
