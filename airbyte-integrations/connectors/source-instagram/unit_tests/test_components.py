# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Dict

from .records import (
    breakdowns_record,
    children_record,
    clear_url_record,
    clear_url_record_transformed,
    expected_breakdown_record_transformed,
    expected_children_transformed,
    insights_record,
    insights_record_transformed,
)


def mock_path(requests_mock, graph_url: str, path: str, method: str = "GET", response: Dict = None):
    complete_url = f"{graph_url}/{path}"
    requests_mock.register_uri(method, complete_url, json=response)


def test_instagram_media_children_transformation(components_module, requests_mock, config):
    graph_url = components_module.GRAPH_URL

    params = "?fields=id,ig_id,media_type,media_url,owner,permalink,shortcode,thumbnail_url,timestamp,username"
    children_record_data = children_record["children"]["data"]
    expected_children_transformed_data = expected_children_transformed["children"]
    for index in range(len(children_record_data)):
        mock_path(
            requests_mock,
            graph_url=graph_url,
            path=f"{children_record_data[index]['id']}{params}",
            response=expected_children_transformed_data[index],
        )

    record_transformation = components_module.InstagramMediaChildrenTransformation()
    transformation_result = record_transformation.transform(children_record, config)
    assert transformation_result == expected_children_transformed


def test_instagram_clear_url_transformation(components_module):
    record_transformation = components_module.InstagramClearUrlTransformation().transform(clear_url_record)
    assert record_transformation == clear_url_record_transformed


def test_break_down_results_transformation(components_module):
    record_transformation_result = components_module.InstagramBreakDownResultsTransformation().transform(breakdowns_record)
    assert record_transformation_result == expected_breakdown_record_transformed


def test_instagram_insights_transformation(components_module, config):
    record_transformation = components_module.InstagramInsightsTransformation().transform(insights_record)
    assert record_transformation == insights_record_transformed
