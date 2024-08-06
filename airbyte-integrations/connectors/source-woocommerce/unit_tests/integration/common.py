from typing import MutableMapping, Any

import source_woocommerce
from airbyte_cdk.connector_builder.connector_builder_handler import resolve_manifest
from airbyte_cdk import AbstractSource


def config() -> MutableMapping[str, Any]:
    return {
        "api_key": "test_api_key",
        "api_secret": "test_api_secret",
        "shop": "airbyte.store",
        "start_date": "2017-01-01",
    }


def source() -> AbstractSource:
    return source_woocommerce.SourceWoocommerce()


def common_params():
    return "orderby=id&order=asc&dates_are_gmt=true&per_page=100"


def endpoint_url(stream_name: str, path_parameter: str = None) -> str:
    if path_parameter:
        return f"{url_base()}/{path_parameter}/{stream_name}"

    return f"{url_base()}/{stream_name}"


def url_base() -> str:
    url = resolve_manifest(source()).record.data["manifest"]["definitions"]["requester"]["url_base"]
    url = url.replace("{{ config['shop'] }}", config()["shop"])
    return url
