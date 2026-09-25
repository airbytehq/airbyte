#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
from pathlib import Path

import pytest
import requests_mock
from conftest import YAML_FILE_PATH

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


_RESOURCE_DIR = Path(__file__).parent / "resource"
_FEED_BODY = (_RESOURCE_DIR / "rss2.xml").read_text()

logger = logging.getLogger("airbyte")


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
        mocker.get(requests_mock.ANY, text=_FEED_BODY)
        try:
            list(source.read(logger, config, catalog, state=None))
        except Exception:
            # Record processing may fail (e.g. record_filter on items without
            # `published`); the URL assertion below is what matters here.
            pass

        assert mocker.request_history, "expected at least one HTTP request"
        assert mocker.request_history[0].url == url
