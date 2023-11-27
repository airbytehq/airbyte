from typing import Tuple, Dict, Any
from unittest import TestCase

from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_protocol.models import SyncMode, ConfiguredAirbyteCatalog

from source_stripe import SourceStripe
from test import CatalogBuilder, create_builders_from_file, HttpMocker, HttpRequestMatcher, RecordBuilder, ResponseBuilder

_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"
_CONFIG = {"client_secret": _CLIENT_SECRET, "account_id": _ACCOUNT_ID, "start_date": "2023-09-28T20:15:00Z"}
_NO_STATE = {}


def stripe_pagination_strategy(response: Dict[str, Any]) -> None:
    response["has_more"] = True


class AccountStreamTest(TestCase):

    def _catalog(self, sync_mode: SyncMode = SyncMode.full_refresh) -> ConfiguredAirbyteCatalog:
        return CatalogBuilder().with_stream("accounts", sync_mode).build()

    def _source(self, catalog: ConfiguredAirbyteCatalog) -> SourceStripe:
        return SourceStripe(catalog)

    @HttpMocker()
    def test_given_one_page_when_read_then_return_record(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequestMatcher(
                url="https://api.stripe.com/v1/accounts",
                query_params={"limit": 100},
                headers={},
            ),
            self._a_response().with_record(self._a_record()).build_json()
        )
        catalog = self._catalog()

        output = read(self._source(catalog), _CONFIG, catalog)

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_many_pages_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequestMatcher(
                url="https://api.stripe.com/v1/accounts",
                query_params={"limit": 100},
                headers={},
            ),
            self._a_response().with_pagination().with_record(self._a_record().with_id("last_record_from_page_id")).build_json()
        )
        http_mocker.get(
            HttpRequestMatcher(
                url="https://api.stripe.com/v1/accounts",
                query_params={"starting_after": "last_record_from_page_id", "limit": 100},
                headers={},
            ),
            self._a_response().with_record(self._a_record()).build_json()
        )
        catalog = self._catalog()

        output = read(self._source(catalog), _CONFIG, catalog)

        assert len(output.records) == 2

    def _a_record(self) -> RecordBuilder:
        return self._create_builders()[0]

    def _a_response(self) -> ResponseBuilder:
        return self._create_builders()[1]

    def _create_builders(self) -> Tuple[RecordBuilder, ResponseBuilder]:
        return create_builders_from_file("accounts", ["data"], ["id"], stripe_pagination_strategy)
