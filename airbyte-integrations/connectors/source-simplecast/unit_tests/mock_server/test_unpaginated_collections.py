# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import get_source

from .config import ConfigBuilder
from .request_builder import SimplecastRequestBuilder
from .response_builder import collection_response


@pytest.mark.parametrize("stream_name,id_field,label_field", [("categories", "value", "label"), ("distribution_channels", "id", "name")])
@pytest.mark.parametrize("collection_size", [19, 0], ids=["full_collection", "empty_collection"])
def test_read_collection_once(stream_name, id_field, label_field, collection_size):
    config = ConfigBuilder().build()
    records = [{id_field: f"{stream_name}-{index}", label_field: f"Label {index}"} for index in range(collection_size)]
    request = SimplecastRequestBuilder.collection(stream_name, config["api_token"])
    with HttpMocker() as http_mocker:
        # Serve the same full collection regardless of offset. The final empty
        # response is only a safety stop so a regressed paginator cannot hang.
        http_mocker.get(request, [collection_response(records), collection_response(records), collection_response([])])
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(config), config=config, catalog=catalog)

        http_mocker.assert_number_of_calls(request, 1)
        assert [message.record.data for message in output.records] == records
        assert [message.record.stream for message in output.records] == [stream_name] * collection_size
        assert output.errors == []
        assert [(sent.method, sent.url) for sent in http_mocker._mocker.request_history] == [
            ("GET", f"https://api.simplecast.com/{stream_name}")
        ]
