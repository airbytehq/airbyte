"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Dict

import shopify
from airbyte_protocol import AirbyteCatalog
from base_python import AirbyteLogger
from base_singer import BaseSingerSource


class SourceShopifySinger(BaseSingerSource):
    """
    Shopify API Reference: https://shopify.dev/docs/admin-api/rest/reference
    """

    tap_cmd = "tap-shopify"
    tap_name = "Shopify API"
    api_error = Exception

    def transform_config(self, raw_config):
        return {
            "start_date": raw_config["start_date"],
            "api_key": raw_config["api_password"],
            "shop": raw_config["shop"],
            "date_window_size": 7,
        }

    def try_connect(self, logger: AirbyteLogger, config: dict):
        session = shopify.Session(f"{config['shop']}.myshopify.com", "2021-01", config["api_key"])
        shopify.ShopifyResource.activate_session(session)
        # try to read the name of the shop, which should be available with any level of permissions
        shopify.GraphQL().execute("{ shop { name id } }")
        shopify.ShopifyResource.clear_session()

    def discover(self, logger: AirbyteLogger, config: Dict[str, any]) -> AirbyteCatalog:
        catalog: AirbyteCatalog = super().discover(logger, config)

        # the metafields stream has a union type i.e: ["null", "integer", "object", "string"], but Airbyte doesn't currently allow the notion of a
        # union type. See https://github.com/airbytehq/airbyte/issues/1864 for more details.
        # For now we always declare this field is a nullable string as an escape hatch.
        for stream in catalog.streams:
            if stream.name == "metafields":
                schema = stream.json_schema
                if "properties" in schema and "value" in schema["properties"]:
                    schema["properties"]["value"]["type"] = ["null", "string"]

        return catalog
