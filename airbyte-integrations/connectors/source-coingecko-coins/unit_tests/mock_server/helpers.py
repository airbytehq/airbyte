# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpRequest

from ..conftest import get_source


def config(api_key: str = "", legacy_dates: bool = False) -> dict:
    return {
        "api_key": api_key,
        "coin_id": "bitcoin",
        "vs_currency": "usd",
        "days": "7",
        "start_date": "01-11-2026" if legacy_dates else "2026-11-01",
        "end_date": "04-11-2026" if legacy_dates else "2026-11-04",
    }


def request(stream: str, api_key: str = "", date: str | None = None) -> HttpRequest:
    params = {"vs_currency": "usd", "days": "7"}
    if api_key:
        params["x_cg_pro_api_key"] = api_key
    if date:
        params["date"] = date
    host = "pro-api" if api_key else "api"
    return HttpRequest(f"https://{host}.coingecko.com/api/v3/coins/bitcoin/{stream}", query_params=params)


def read_stream(
    stream: str,
    config: dict,
    mode: SyncMode = SyncMode.full_refresh,
    state: list[AirbyteStateMessage] | None = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream, mode).build()
    return read(get_source(config, state), config, catalog, state=state, expecting_exception=expecting_exception)
