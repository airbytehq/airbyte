#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
import re

import pytest
from source_rss import SourceRss

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)


RSS_BODY = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test feed</title>
    <link>https://example.com/</link>
    <description>Test feed</description>
    <item>
      <title>Test item</title>
      <link>https://example.com/item</link>
      <guid>test-item</guid>
      <pubDate>Wed, 01 Jan 2025 00:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/feed/?key=test123",
        "https://example.com/feed.xml",
        "https://example.com/rss?a=1&b=2",
    ],
)
def test_items_stream_requests_configured_url_verbatim(requests_mock, url):
    requests_mock.get(re.compile(r"https://example\.com/.*"), text=RSS_BODY)
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="items",
                    json_schema={},
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )

    list(SourceRss().read(logging.getLogger("source_rss"), {"url": url}, catalog))

    assert requests_mock.request_history[0].url == url
