# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, MutableMapping, Optional

import source_woocommerce
from airbyte_cdk import AbstractSource
from airbyte_cdk.connector_builder.connector_builder_handler import resolve_manifest


def config() -> MutableMapping[str, Any]:
    return {
        "api_key": "test_api_key",
        "api_secret": "test_api_secret",
        "shop": "airbyte.store",
        "start_date": "2017-01-01",
    }


def source() -> AbstractSource:
    return source_woocommerce.SourceWoocommerce()


def url_base() -> str:
    url = resolve_manifest(source()).record.data["manifest"]["definitions"]["requester"]["url_base"]
    url = url.replace("{{ config['shop'] }}", config()["shop"])
    return url


def common_params():
    return "orderby=id&order=asc&dates_are_gmt=true&per_page=100"


def build_url(resource_path: str, is_regex: bool = False, modified_after: str = None, modified_before: str = None) -> str:
    """Build a URL for a WooCommerce API endpoint."""
    separator = "." if is_regex else "?"
    url = f"{url_base()}/{resource_path}{separator}{common_params()}"
    if modified_after:
        url = f"{url}&modified_after={modified_after}"
    if modified_before:
        url = f"{url}&modified_before={modified_before}"

    return url
