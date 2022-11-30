#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping
from unittest.mock import MagicMock

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from source_typeform.source import Forms, Images, Responses, Themes, TypeformStream, Webhooks, Workspaces

logger = AirbyteLogger()

TYPEFORM_BASE_URL = TypeformStream.url_base


def merge_records(stream: TypeformStream, sync_mode: SyncMode) -> List[Mapping[str, Any]]:
    merged_records = []
    for stream_slice in stream.stream_slices(sync_mode=sync_mode):
        records = stream.read_records(sync_mode=sync_mode, stream_slice=stream_slice)
        for record in records:
            merged_records.append(record)

    return merged_records


def test_stream_forms_configured(requests_mock, config, form_response):
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/u6nXL7", form_response)
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/k9xNV4", form_response)

    stream = Forms(authenticator=MagicMock(), **config)

    merged_records = merge_records(stream, SyncMode.full_refresh)

    assert len(merged_records) == 2


def test_stream_forms_unconfigured(requests_mock, config_without_forms, forms_response, form_response):
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/u6nXL7", form_response)
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/k9xNV4", form_response)
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms?page_size=200&page=1", forms_response)

    stream = Forms(authenticator=MagicMock(), **config_without_forms)

    merged_records = merge_records(stream, SyncMode.full_refresh)

    assert len(merged_records) == 2


def test_stream_responses_configured(requests_mock, config, response_response):
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/u6nXL7/responses", response_response)
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/k9xNV4/responses", response_response)

    stream = Responses(authenticator=MagicMock(), **config)

    merged_records = merge_records(stream, SyncMode.incremental)

    assert len(merged_records) == 8


def test_stream_responses_unconfigured(requests_mock, config_without_forms, forms_response, response_response):
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/u6nXL7/responses", response_response)
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/k9xNV4/responses", response_response)
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms?page_size=200&page=1", forms_response)

    stream = Responses(authenticator=MagicMock(), **config_without_forms)

    merged_records = merge_records(stream, SyncMode.incremental)

    assert len(merged_records) == 8


def test_stream_webhooks(requests_mock, config, forms_response, webhooks_response):
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/u6nXL7/webhooks", webhooks_response)
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/k9xNV4/webhooks", webhooks_response)
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms?page_size=200&page=1", forms_response)

    stream = Webhooks(authenticator=MagicMock(), **config)

    merged_records = merge_records(stream, SyncMode.full_refresh)

    assert len(merged_records) == 2


def test_stream_workspaces(requests_mock, config, workspaces_response):
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "workspaces?page=1&page_size=200", workspaces_response)

    stream = Workspaces(authenticator=MagicMock(), **config)

    merged_records = merge_records(stream, SyncMode.full_refresh)

    assert len(merged_records) == 2


def test_stream_images(requests_mock, config, images_response):
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "images", images_response)

    stream = Images(authenticator=MagicMock(), **config)

    merged_records = merge_records(stream, SyncMode.full_refresh)

    assert len(merged_records) == 2


def test_stream_themes(requests_mock, config, themes_response):
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "themes?page=1&page_size=200", themes_response)

    stream = Themes(authenticator=MagicMock(), **config)

    merged_records = merge_records(stream, SyncMode.full_refresh)

    assert len(merged_records) == 2
