# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


import pytest
from source_shopify.shopify_graphql.bulk.exceptions import ShopifyBulkExceptions
from source_shopify.shopify_graphql.bulk.tools import BulkTools


def test_camel_to_snake() -> None:
    assert BulkTools.camel_to_snake("camelCase") == "camel_case"
    assert BulkTools.camel_to_snake("snake_case") == "snake_case"
    assert BulkTools.camel_to_snake("PascalCase") == "pascal_case"


@pytest.mark.parametrize(
    "job_result_url, error_type, expected",
    [
        (
            "https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/<some_hashed_sum>?GoogleAccessId=assets-us-prod%40shopify-tiers.iam.gserviceaccount.com&Expires=1705508208&Signature=<some_long_signature>%3D%3D&response-content-disposition=attachment%3B+filename%3D%22bulk-4147374162109.jsonl%22%3B+filename%2A%3DUTF-8%27%27bulk-4147374162109.jsonl&response-content-type=application%2Fjsonl",
            None,
            "bulk-4147374162109.jsonl",
        ),
        (
            "https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/<some_hashed_sum>?GoogleAccessId=assets-us-prod%40shopify-tiers.iam.gserviceaccount.com&Expires=1705508208",
            ShopifyBulkExceptions.BulkJobResultUrlError,
            "Could not extract the `filename` from `result_url` provided",
        ),
    ],
    ids=["success", "error"],
)
def test_filename_from_url(job_result_url, error_type, expected) -> None:
    if error_type:
        with pytest.raises(error_type) as error:
            BulkTools.filename_from_url(job_result_url)
        assert expected in repr(error.value)
    else:
        assert BulkTools.filename_from_url(job_result_url) == expected


def test_from_iso8601_to_rfc3339() -> None:
    record = {"date": "2023-01-01T15:00:00Z"}
    assert BulkTools.from_iso8601_to_rfc3339(record, "date") == "2023-01-01T15:00:00+00:00"


def test_fields_names_to_snake_case() -> None:
    dict_input = {"camelCase": "value", "snake_case": "value", "__parentId": "value"}
    expected_output = {"camel_case": "value", "snake_case": "value", "__parentId": "value"}
    assert BulkTools().fields_names_to_snake_case(dict_input) == expected_output


def test_resolve_str_id() -> None:
    assert BulkTools.resolve_str_id("123") == 123
    assert BulkTools.resolve_str_id("456", str) == "456"
    assert BulkTools.resolve_str_id(None) is None
