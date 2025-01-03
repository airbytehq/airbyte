#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus
from typing import Any, List, Mapping, Optional

from source_amazon_seller_partner import SourceAmazonSellerPartner

from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import _get_unit_test_folder
from airbyte_protocol.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, Level, SyncMode

from .config import ACCESS_TOKEN, ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import build_response


def config() -> ConfigBuilder:
    return ConfigBuilder()


def catalog(stream_name: str, sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def source() -> SourceAmazonSellerPartner:
    return SourceAmazonSellerPartner()


def read_output(
    config_builder: ConfigBuilder,
    stream_name: str,
    sync_mode: SyncMode,
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: Optional[bool] = False,
) -> EntrypointOutput:
    _catalog = catalog(stream_name, sync_mode)
    _config = config_builder.build()
    return read(source(), _config, _catalog, state, expecting_exception)


def get_stream_by_name(stream_name: str, config_: Mapping[str, Any]) -> Stream:
    streams = [stream for stream in source().streams(config_) if stream.name == stream_name]
    if not streams:
        raise ValueError("Please provide a valid stream name")
    return streams[0]


def find_template(resource: str, execution_folder: str, template_format: Optional[str] = "csv") -> str:
    response_template_filepath = str(
        # FIXME: the below function should be replaced with the public version after next CDK release
        _get_unit_test_folder(execution_folder) / "resource" / "http" / "response" / f"{resource}.{template_format}"
    )
    with open(response_template_filepath, "r") as template_file:
        if template_file == "json":
            return json.load(template_file)
        else:
            return template_file.read()


def mock_auth(http_mocker: HttpMocker) -> None:
    response_body = {"access_token": ACCESS_TOKEN, "expires_in": 3600, "token_type": "bearer"}
    http_mocker.post(RequestBuilder.auth_endpoint().build(), build_response(response_body, status_code=HTTPStatus.OK))


def assert_message_in_log_output(message: str, entrypoint_output: EntrypointOutput, log_level: Optional[Level] = Level.WARN) -> None:
    assert any(
        message in airbyte_message.log.message for airbyte_message in entrypoint_output.logs if airbyte_message.log.level == log_level
    )
