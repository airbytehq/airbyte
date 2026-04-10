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
        ),
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


class TestComponentStreamingCap:
    """Tests for the 500-component streaming cap that prevents OOM on parents with many components."""

    def _make_record_instance(self, basic_config, threshold=5, supports_component_streaming=True):
        """Helper to create a ShopifyBulkRecord with a low threshold for testing."""
        _Query = type(
            "_Query",
            (ShopifyBulkQuery,),
            {
                "supports_component_streaming": supports_component_streaming,
                "query_name": "customers",
            },
        )
        query = _Query(basic_config)
        record_instance = ShopifyBulkRecord(query)
        record_instance.composition = {"new_record": "Customer", "record_components": ["Metafield"]}
        record_instance.components = ["Metafield"]
        record_instance._component_streaming_threshold = threshold
        return record_instance

    def test_component_count_empty_buffer(self, basic_config):
        record_instance = self._make_record_instance(basic_config)
        assert record_instance._component_count() == 0

    def test_component_count_with_components(self, basic_config):
        record_instance = self._make_record_instance(basic_config)
        record_instance.record_new({"__typename": "Customer", "id": "gid://shopify/Customer/1", "name": "Alice"})
        for i in range(3):
            record_instance.record_new_component({"__typename": "Metafield", "id": f"gid://shopify/Metafield/{i}"})
        assert record_instance._component_count() == 3

    def test_should_flush_below_threshold(self, basic_config):
        record_instance = self._make_record_instance(basic_config, threshold=5)
        record_instance.record_new({"__typename": "Customer", "id": "gid://shopify/Customer/1", "name": "Alice"})
        for i in range(4):
            record_instance.record_new_component({"__typename": "Metafield", "id": f"gid://shopify/Metafield/{i}"})
        assert not record_instance._should_flush_components()

    def test_should_flush_at_threshold(self, basic_config):
        record_instance = self._make_record_instance(basic_config, threshold=5)
        record_instance.record_new({"__typename": "Customer", "id": "gid://shopify/Customer/1", "name": "Alice"})
        for i in range(5):
            record_instance.record_new_component({"__typename": "Metafield", "id": f"gid://shopify/Metafield/{i}"})
        assert record_instance._should_flush_components()

    def test_partial_flush_emits_records_and_re_registers_parent(self, basic_config):
        """When component count hits threshold, record_compose should flush and re-register parent."""
        record_instance = self._make_record_instance(basic_config, threshold=3)

        # register parent — no output expected
        result = list(record_instance.record_compose({"__typename": "Customer", "id": "gid://shopify/Customer/1", "name": "Alice"}))
        assert result == []
        assert len(record_instance.buffer) == 1

        # add components 0, 1 — below threshold, no flush
        for i in range(2):
            result = list(
                record_instance.record_compose({"__typename": "Metafield", "id": f"gid://shopify/Metafield/{i}", "value": f"val{i}"})
            )
            assert result == []

        # add component 2 — hits threshold (3), should partial flush
        flushed = list(record_instance.record_compose({"__typename": "Metafield", "id": "gid://shopify/Metafield/2", "value": "val2"}))
        # buffer_flush yields records via record_process_components (default: yield record as-is)
        assert len(flushed) == 1
        # the flushed record should contain the 3 metafields
        assert len(flushed[0]["record_components"]["Metafield"]) == 3

        # parent should be re-registered with empty components
        assert len(record_instance.buffer) == 1
        assert record_instance.buffer[0]["record_components"]["Metafield"] == []
        # parent fields should be preserved (id gets resolved to int by buffer_flush)
        assert record_instance.buffer[0]["name"] == "Alice"

    def test_subsequent_components_attach_after_partial_flush(self, basic_config):
        """After a partial flush, new components should attach to the re-registered parent."""
        record_instance = self._make_record_instance(basic_config, threshold=2)

        # register parent
        list(record_instance.record_compose({"__typename": "Customer", "id": "gid://shopify/Customer/1", "name": "Alice"}))

        # add 2 components → triggers partial flush
        list(record_instance.record_compose({"__typename": "Metafield", "id": "gid://shopify/Metafield/0", "value": "v0"}))
        flushed1 = list(record_instance.record_compose({"__typename": "Metafield", "id": "gid://shopify/Metafield/1", "value": "v1"}))
        assert len(flushed1) == 1

        # add 1 more component — should attach to re-registered parent
        result = list(record_instance.record_compose({"__typename": "Metafield", "id": "gid://shopify/Metafield/2", "value": "v2"}))
        # below threshold again, so no flush
        assert result == []
        assert len(record_instance.buffer) == 1
        assert len(record_instance.buffer[0]["record_components"]["Metafield"]) == 1
        assert record_instance.buffer[0]["record_components"]["Metafield"][0]["value"] == "v2"

    def test_multiple_partial_flushes_same_parent(self, basic_config):
        """Multiple partial flushes should work for the same parent."""
        record_instance = self._make_record_instance(basic_config, threshold=2)

        # register parent
        list(record_instance.record_compose({"__typename": "Customer", "id": "gid://shopify/Customer/1", "name": "Alice"}))

        all_flushed = []
        # add 6 components total → should trigger 3 partial flushes at indices 1, 3, 5
        for i in range(6):
            flushed = list(
                record_instance.record_compose({"__typename": "Metafield", "id": f"gid://shopify/Metafield/{i}", "value": f"v{i}"})
            )
            all_flushed.extend(flushed)

        # 3 partial flushes, each with 2 metafields
        assert len(all_flushed) == 3
        for record in all_flushed:
            assert len(record["record_components"]["Metafield"]) == 2

        # buffer should have the re-registered parent with empty components
        assert len(record_instance.buffer) == 1
        assert record_instance.buffer[0]["record_components"]["Metafield"] == []

    def test_new_parent_flushes_previous_parent_remaining(self, basic_config):
        """When a new parent arrives, it should flush the remaining buffer from the previous parent."""
        record_instance = self._make_record_instance(basic_config, threshold=5)

        # register parent 1 and add 3 components (below threshold)
        list(record_instance.record_compose({"__typename": "Customer", "id": "gid://shopify/Customer/1", "name": "Alice"}))
        for i in range(3):
            list(record_instance.record_compose({"__typename": "Metafield", "id": f"gid://shopify/Metafield/{i}", "value": f"v{i}"}))

        # new parent 2 should flush parent 1's buffer
        flushed = list(record_instance.record_compose({"__typename": "Customer", "id": "gid://shopify/Customer/2", "name": "Bob"}))
        assert len(flushed) == 1
        assert len(flushed[0]["record_components"]["Metafield"]) == 3

        # buffer now has parent 2
        assert len(record_instance.buffer) == 1
        assert record_instance.buffer[0]["name"] == "Bob"

    def test_threshold_configurable_via_env_var(self, basic_config, monkeypatch):
        """The threshold should be configurable via BULK_COMPONENT_STREAMING_THRESHOLD env var."""
        monkeypatch.setenv("BULK_COMPONENT_STREAMING_THRESHOLD", "3")
        query = ShopifyBulkQuery(basic_config)
        record_instance = ShopifyBulkRecord(query)
        assert record_instance._component_streaming_threshold == 3

    def test_default_threshold_is_500(self, basic_config, monkeypatch):
        """Without env var override, the default threshold should be 500."""
        monkeypatch.delenv("BULK_COMPONENT_STREAMING_THRESHOLD", raising=False)
        query = ShopifyBulkQuery(basic_config)
        record_instance = ShopifyBulkRecord(query)
        assert record_instance._component_streaming_threshold == 500

    def test_no_partial_flush_when_component_streaming_disabled(self, basic_config):
        """When `supports_component_streaming` is False, no partial flush should occur even above threshold."""
        record_instance = self._make_record_instance(basic_config, threshold=2, supports_component_streaming=False)

        # register parent
        list(record_instance.record_compose({"__typename": "Customer", "id": "gid://shopify/Customer/1", "name": "Alice"}))

        # add 4 components — exceeds threshold of 2, but streaming is disabled
        all_flushed = []
        for i in range(4):
            flushed = list(
                record_instance.record_compose({"__typename": "Metafield", "id": f"gid://shopify/Metafield/{i}", "value": f"v{i}"})
            )
            all_flushed.extend(flushed)

        # no partial flushes should have occurred
        assert all_flushed == []
        # all 4 components should still be buffered under the single parent
        assert len(record_instance.buffer) == 1
        assert len(record_instance.buffer[0]["record_components"]["Metafield"]) == 4
