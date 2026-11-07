#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

import pytest
import requests_mock
from conftest import YAML_FILE_PATH

from airbyte_cdk.models import SyncMode, Type
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


logger = logging.getLogger("airbyte")


def _feed_body() -> str:
    pub_date = format_datetime(datetime.now(timezone.utc) - timedelta(minutes=5))
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com</link>
    <description>Test</description>
    <item>
      <title>Recent Item One</title>
      <link>https://example.com/1</link>
      <guid>https://example.com/1</guid>
      <pubDate>{pub_date}</pubDate>
    </item>
    <item>
      <title>Recent Item Two</title>
      <link>https://example.com/2</link>
      <guid>https://example.com/2</guid>
      <pubDate>{pub_date}</pubDate>
    </item>
  </channel>
</rss>
"""


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/feed/?key=test123",
        "https://example.com/feed?key=test123&format=rss",
        "https://example.com/breaking_news.rss",
        "https://example.com/feed/",
    ],
)
def test_feed_url_is_used_verbatim(url):
    """The configured feed URL must be requested exactly as given.

    Regression test: older CDK versions joined the url_base with the stream path
    via os.path.join(..., ""), appending a spurious trailing slash.
    """
    config = {"url": url}
    catalog = CatalogBuilder().with_stream("items", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(YAML_FILE_PATH),
        catalog=catalog,
        config=config,
        state=StateBuilder().build(),
    )

    with requests_mock.Mocker(real_http=False) as mocker:
        mocker.get(requests_mock.ANY, text=_feed_body())
        messages = list(source.read(logger, config, catalog, state=None))

        assert mocker.request_history, "expected at least one HTTP request"
        assert mocker.request_history[0].url == url

    records = [m.record.data for m in messages if m.type == Type.RECORD]
    assert records, "expected at least one record from the feed"
    assert all("published" in record for record in records)
