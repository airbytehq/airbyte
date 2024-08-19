# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


import pytest
from source_shopify.shopify_graphql.bulk.query import ShopifyBulkQuery
from source_shopify.shopify_graphql.bulk.record import ShopifyBulkRecord


@pytest.mark.parametrize(
    "record, expected",
    [
        (
            {"id": "gid://shopify/Order/19435458986123"},
            {"id": 19435458986123, "admin_graphql_api_id": "gid://shopify/Order/19435458986123"},
        ),
        ({"id": 123}, {"id": 123}),
    ],
)
def test_record_resolve_id(basic_config, record, expected) -> None:
    bulk_query = ShopifyBulkQuery(basic_config)
    assert ShopifyBulkRecord(bulk_query).record_resolve_id(record) == expected


@pytest.mark.parametrize(
    "record, types, expected",
    [
        ({"__typename": "Order", "id": "gid://shopify/Order/19435458986123"}, ["Test", "Order"], True),
        ({"__typename": "Test", "id": "gid://shopify/Order/19435458986123"}, "Other", False),
        ({}, "Other", False),
    ],
)
def test_check_type(basic_config, record, types, expected) -> None:
    query = ShopifyBulkQuery(basic_config)
    assert ShopifyBulkRecord(query).check_type(record, types) == expected


@pytest.mark.parametrize(
    "record, expected",
    [
        (
            {
                "id": "gid://shopify/Metafield/123",
                "__parentId": "gid://shopify/Order/102030",
            },
            {
                "id": 123,
                "admin_graphql_api_id": "gid://shopify/Metafield/123",
                "__parentId": "gid://shopify/Order/102030",
            },
        ),
        (
            {
                "alias_to_id_field": "gid://shopify/Metafield/123",
                "__parentId": "gid://shopify/Order/102030",
            },
            # should be emitted `as is`, because the `id` field in not present
            {
                "alias_to_id_field": "gid://shopify/Metafield/123",
                "__parentId": "gid://shopify/Order/102030",
            },
        )
    ],
)
def test_record_resolver(basic_config, record, expected) -> None:
    query = ShopifyBulkQuery(basic_config)
    record_instance = ShopifyBulkRecord(query)
    assert record_instance.record_resolve_id(record) == expected


@pytest.mark.parametrize(
    "record, expected",
    [
        (
            {"id": "gid://shopify/Order/1234567890", "__typename": "Order"},
            {"id": "gid://shopify/Order/1234567890"},
        ),
    ],
)
def test_record_new(basic_config, record, expected) -> None:
    query = ShopifyBulkQuery(basic_config)
    record_instance = ShopifyBulkRecord(query)
    record_instance.record_new(record)
    assert record_instance.buffer == [expected]


@pytest.mark.parametrize(
    "records_from_jsonl, record_components, expected",
    [
        (
            [
                {"__typename": "NewRecord", "id": "gid://shopify/NewRecord/1234567890", "name": "new_record"},
                {"__typename": "RecordComponent", "id": "gid://shopify/RecordComponent/1234567890", "name": "new_component"},
            ],
            {"new_record": "NewRecord", "record_components": ["RecordComponent"]},
            [
                {
                    "id": "gid://shopify/NewRecord/1234567890",
                    "name": "new_record",
                    "record_components": {
                        "RecordComponent": [
                            {
                                "id": "gid://shopify/RecordComponent/1234567890",
                                "name": "new_component",
                            },
                        ]
                    },
                }
            ],
        ),
    ],
    ids=["add_component"],
)
def test_record_new_component(basic_config, records_from_jsonl, record_components, expected) -> None:
    query = ShopifyBulkQuery(basic_config)
    record_instance = ShopifyBulkRecord(query)
    record_instance.components = record_components.get("record_components")
    # register new record first
    record_instance.record_new(records_from_jsonl[0])
    assert len(record_instance.buffer) > 0
    # check the components placeholder was created for new record registered
    assert "record_components" in record_instance.buffer[-1].keys()
    # register record component
    record_instance.record_new_component(records_from_jsonl[1])
    # check the component was proccessed
    assert len(record_instance.buffer[-1]["record_components"]["RecordComponent"]) > 0
    # general check
    assert record_instance.buffer == expected


@pytest.mark.parametrize(
    "buffered_record, expected",
    [
        (
            {
                "id": "gid://shopify/NewRecord/1234567890",
                "name": "new_record",
                "record_components": {
                    "RecordComponent": [
                        {
                            "id": "gid://shopify/RecordComponent/1234567890",
                            "name": "new_component",
                        }
                    ]
                },
            },
            [
                {
                    "id": 1234567890,
                    "name": "new_record",
                    "record_components": {
                        "RecordComponent": [
                            {
                                "id": "gid://shopify/RecordComponent/1234567890",
                                "name": "new_component",
                            },
                        ]
                    },
                    "admin_graphql_api_id": "gid://shopify/NewRecord/1234567890",
                }
            ],
        ),
    ],
)
def test_buffer_flush(basic_config, buffered_record, expected) -> None:
    query = ShopifyBulkQuery(basic_config)
    record_instance = ShopifyBulkRecord(query)
    # populate the buffer with record
    record_instance.buffer.append(buffered_record)
    assert list(record_instance.buffer_flush()) == expected


@pytest.mark.parametrize(
    "records_from_jsonl, record_composition, expected",
    [
        (
            [
                {"__typename": "NewRecord", "id": "gid://shopify/NewRecord/1234567890", "name": "new_record"},
                {"__typename": "RecordComponent", "id": "gid://shopify/RecordComponent/1234567890", "name": "new_component"},
            ],
            {"new_record": "NewRecord", "record_components": ["RecordComponent"]},
            [
                {
                    "id": "gid://shopify/NewRecord/1234567890",
                    "name": "new_record",
                    "record_components": {
                        "RecordComponent": [
                            {
                                "id": "gid://shopify/RecordComponent/1234567890",
                                "name": "new_component",
                            },
                        ]
                    },
                }
            ],
        ),
    ],
    ids=["test_compose"],
)
def test_record_compose(basic_config, records_from_jsonl, record_composition, expected) -> None:
    query = ShopifyBulkQuery(basic_config)
    # query.record_composition = record_composition
    record_instance = ShopifyBulkRecord(query)
    record_instance.composition = record_composition
    record_instance.components = record_composition.get("record_components")
    # process read jsonl records
    for record in records_from_jsonl:
        list(record_instance.record_compose(record))

    assert record_instance.buffer == expected
