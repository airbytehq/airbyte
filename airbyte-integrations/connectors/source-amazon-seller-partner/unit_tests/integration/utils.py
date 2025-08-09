#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus
from pathlib import Path
from typing import Any, List, Mapping, Optional
from unittest.mock import Mock

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, Level, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.test.utils.data import get_unit_test_folder

from ..conftest import get_source
from .config import ACCESS_TOKEN, ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import build_response


_YAML_FILE_PATH = Path(__file__).parent.parent.parent / "manifest.yaml"


def config() -> ConfigBuilder:
    return ConfigBuilder()


def catalog(stream_name: str, sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def source(
    catalog: ConfiguredAirbyteCatalog,
    config: Mapping[str, Any],
    state: Optional[List[AirbyteStateMessage]] = None,
) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state or StateBuilder().build())


def read_output(
    config_builder: ConfigBuilder,
    stream_name: str,
    sync_mode: SyncMode,
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: Optional[bool] = False,
) -> EntrypointOutput:
    _catalog = catalog(stream_name, sync_mode)
    _config = config_builder.build()
    _source = source(catalog=_catalog, config=_config, state=state)
    _source.write_config = Mock()
    # This ensures the transformed config is used
    _config = _source.configure(config=_config, temp_dir="/fake/path/config.json")
    return read(_source, _config, _catalog, state, expecting_exception, debug=True)


def get_stream_by_name(stream_name: str, config_: Mapping[str, Any]) -> Stream:
    source = get_source(config_, config_path=None)
    streams = [stream for stream in source.streams(source._config) if stream.name == stream_name]
    if not streams:
        raise ValueError("Please provide a valid stream name")
    return streams[0]


def find_template(resource: str, execution_folder: str, template_format: Optional[str] = "csv") -> str:
    response_template_filepath = str(
        get_unit_test_folder(execution_folder) / "resource" / "http" / "response" / f"{resource}.{template_format}"
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
