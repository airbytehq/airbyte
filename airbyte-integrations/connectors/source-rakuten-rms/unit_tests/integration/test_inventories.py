# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Mapping, Optional
from unittest import TestCase

import freezegun
from airbyte_cdk.sources.source import TState
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_protocol.models import ConfiguredAirbyteCatalog, SyncMode
from source_rakuten_rms import SourceRakutenRms

_A_CONFIG = {
    "token": "token"
}
_NOW = datetime.now(timezone.utc)

@freezegun.freeze_time(_NOW.isoformat())
class FullRefreshTest(TestCase):

    @HttpMocker()
    def test_read_single_pages(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
        HttpRequest(
            url=f"https://api.rms.rakuten.co.jp/es/2.1/inventories/bulk-get/range?minQuantity=400&maxQuantity=499",
        ),
        HttpResponse(body="""
            {
                "inventories": [
                    {
                        "manageNumber": "4580235733684",
                        "variantId": "4580235733684",
                        "quantity": 450,
                        "created": "2023-07-10T12:27:53+09:00",
                        "updated": "2024-12-05T17:49:53+09:00"
                    },
                    {
                        "manageNumber": "wb25_collab",
                        "variantId": "T25N0088CF1M0_C",
                        "quantity": 412,
                        "created": "2024-07-02T19:21:48+09:00",
                        "updated": "2024-12-05T17:22:59+09:00"
                    },
                    {
                        "manageNumber": "wb25_collab",
                        "variantId": "4582660482526",
                        "quantity": 412,
                        "created": "2024-07-02T19:21:48+09:00",
                        "updated": "2024-12-05T17:22:59+09:00"
                    },
                    {
                        "manageNumber": "wb24_colors_4m",
                        "variantId": "4580235733684",
                        "quantity": 451,
                        "created": "2024-12-02T21:34:28+09:00",
                        "updated": "2024-12-05T17:22:59+09:00"
                    },
                    {
                        "manageNumber": "wb24_tie_4m",
                        "variantId": "4580235733684",
                        "quantity": 451,
                        "created": "2024-12-02T21:34:28+09:00",
                        "updated": "2024-12-05T17:22:59+09:00"
                    },
                    {
                        "manageNumber": "wb24_kitamura_4m",
                        "variantId": "4580235733684",
                        "quantity": 451,
                        "created": "2024-12-02T21:34:28+09:00",
                        "updated": "2024-12-05T17:22:59+09:00"
                    },
                    {
                        "manageNumber": "wb24_shibata_4m",
                        "variantId": "4580235733684",
                        "quantity": 451,
                        "created": "2024-12-02T21:50:34+09:00",
                        "updated": "2024-12-05T17:22:59+09:00"
                    },
                    {
                        "manageNumber": "wb24_kitagishi_4m",
                        "variantId": "4580235733684",
                        "quantity": 451,
                        "created": "2024-12-02T21:34:28+09:00",
                        "updated": "2024-12-05T17:22:59+09:00"
                    },
                    {
                        "manageNumber": "wb24_makino_4m",
                        "variantId": "4580235733684",
                        "quantity": 451,
                        "created": "2024-12-02T21:50:34+09:00",
                        "updated": "2024-12-05T17:22:59+09:00"
                    },
                    {
                        "manageNumber": "wb24_opmlts_4m",
                        "variantId": "4580235733684",
                        "quantity": 451,
                        "created": "2024-12-02T21:34:28+09:00",
                        "updated": "2024-12-05T17:22:59+09:00"
                    },
                    {
                        "manageNumber": "wb24_mothersum_4m",
                        "variantId": "4580235733684",
                        "quantity": 451,
                        "created": "2024-12-02T17:10:27+09:00",
                        "updated": "2024-12-05T17:22:59+09:00"
                    },
                    {
                        "manageNumber": "wb24_shirtrplaid_4m",
                        "variantId": "4580235733684",
                        "quantity": 451,
                        "created": "2024-12-02T21:34:28+09:00",
                        "updated": "2024-12-05T17:22:59+09:00"
                    },
                    {
                        "manageNumber": "wb24_nishikawa_4m",
                        "variantId": "4580235733684",
                        "quantity": 451,
                        "created": "2024-12-02T21:50:34+09:00",
                        "updated": "2024-12-05T17:22:59+09:00"
                    },
                    {
                        "manageNumber": "wb24_libertyemma_4m",
                        "variantId": "4580235733684",
                        "quantity": 451,
                        "created": "2024-12-02T21:34:28+09:00",
                        "updated": "2024-12-05T17:22:59+09:00"
                    },
                    {
                        "manageNumber": "wb25_kusano",
                        "variantId": "4582660482526",
                        "quantity": 412,
                        "created": "2024-08-26T00:55:19+09:00",
                        "updated": "2024-12-05T16:51:24+09:00"
                    }
                ]
            }
        """, status_code=200)
        )
        output = self._read(_A_CONFIG, _configured_catalog("inventories", SyncMode.full_refresh))

        # レスポンスが期待通りか確認
        assert len(output.records) == 15
    
    def _read(self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, configured_catalog=configured_catalog, expecting_exception=expecting_exception)

def _read(
    config: Mapping[str, Any],
    configured_catalog: ConfiguredAirbyteCatalog,
    state: Optional[Dict[str, Any]] = None,
    expecting_exception: bool = False
) -> EntrypointOutput:
    return read(_source(configured_catalog, config, state), config, configured_catalog, state, expecting_exception)


def _configured_catalog(stream_name: str, sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[TState]) -> SourceRakutenRms:
    return SourceRakutenRms(config=config, state=state)