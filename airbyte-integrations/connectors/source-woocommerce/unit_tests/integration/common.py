from typing import MutableMapping, Any, Optional

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


def endpoint_url(stream_name: str, custom_resource_path: Optional[str] = None, path_parameter: Optional[str] = None) -> str:
    url = url_base()
    resource_path = stream_name

    if custom_resource_path:
        resource_path = custom_resource_path

    if path_parameter:
        return f"{url}/{path_parameter}/{resource_path}"

    return f"{url}/{resource_path}"


def url_base() -> str:
    url = resolve_manifest(source()).record.data["manifest"]["definitions"]["requester"]["url_base"]
    url = url.replace("{{ config['shop'] }}", config()["shop"])
    return url
