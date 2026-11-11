#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock as rm
from source_facebook_pages.source import SourceFacebookPages

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


CONFIG = {"page_id": "1", "access_token": "token"}
ACCESS_TOKEN_URL = "https://graph.facebook.com/1?fields=access_token&access_token=token"
INSIGHT = {"name": "m", "period": "lifetime", "values": [{"value": 1}], "id": "1/insights/m/lifetime"}


def _requested(stream, path, param, edge, config):
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    url = f"https://graph.facebook.com/v26.0/1/{path}"
    body = {"data": [INSIGHT]} if edge is None else {"data": [{"id": "9", edge: {"data": [INSIGHT]}}], "paging": {}}
    with rm.Mocker() as m:
        m.get(ACCESS_TOKEN_URL, json={"access_token": "access"})
        m.get(url, json=body)
        output = read(SourceFacebookPages(catalog=catalog, config=config), config, catalog)
        request = next(r for r in m.request_history if urlparse(r.url).path == f"/v26.0/1/{path}")
    assert len(output.records) == 1
    return parse_qs(urlparse(request.url).query)[param][0]


STREAMS = [
    ("page_insights", "insights", "metric", None, "{}", "page_total_actions,page_post_engagements"),
    ("post_insights", "feed", "fields", "insights", "insights.metric({})", "post_media_view,post_total_media_view_unique"),
    ("video_insights", "videos", "fields", "video_insights", "video_insights.metric({})", "total_video_views,total_video_complete_views"),
    ("reel_insights", "video_reels", "fields", "video_insights", "video_insights.metric({})", "blue_reels_play_count,fb_reels_total_plays"),
]


@pytest.mark.parametrize("stream,path,param,edge,template,default_prefix", STREAMS)
def test_insights_streams_use_default_metrics(stream, path, param, edge, template, default_prefix):
    assert _requested(stream, path, param, edge, CONFIG).startswith(template.format(default_prefix).rstrip(")"))


@pytest.mark.parametrize("stream,path,param,edge,template,default_prefix", STREAMS)
def test_insights_streams_use_configured_metrics(stream, path, param, edge, template, default_prefix):
    config = {**CONFIG, f"{stream}_metrics": ["metric_a", "metric_b"]}
    assert _requested(stream, path, param, edge, config) == template.format("metric_a,metric_b")


@pytest.mark.parametrize("stream,path,param,edge,template,default_prefix", STREAMS)
def test_empty_metric_list_falls_back_to_defaults(stream, path, param, edge, template, default_prefix):
    config = {**CONFIG, f"{stream}_metrics": []}
    assert _requested(stream, path, param, edge, config).startswith(template.format(default_prefix).rstrip(")"))
