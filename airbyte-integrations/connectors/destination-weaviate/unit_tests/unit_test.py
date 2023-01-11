#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import uuid
from unittest.mock import Mock

from destination_weaviate.client import Client
from destination_weaviate.utils import generate_id, stream_to_class_name


def test_client_custom_vectors_config():
    mock_object = Client
    mock_object.get_weaviate_client = Mock(return_value=None)
    c = Client({"vectors": "my_table.test", "url": "http://test"}, schema={})
    assert c.vectors["my_table"] == "test", "Single vector should work"

    c = Client({"vectors": "case2.test, another_table.vector", "url": "http://test"}, schema={})
    assert c.vectors["case2"] == "test", "Multiple values case2 should work too"
    assert c.vectors["another_table"] == "vector", "Multiple values another_table should work too"


def test_client_custom_id_schema_config():
    mock_object = Client
    mock_object.get_weaviate_client = Mock(return_value=None)
    c = Client({"id_schema": "my_table.my_id", "url": "http://test"}, schema={})
    assert c.id_schema["my_table"] == "my_id", "Single id_schema definition should work"

    c = Client({"id_schema": "my_table.my_id, another_table.my_id2", "url": "http://test"}, schema={})
    assert c.id_schema["my_table"] == "my_id", "Multiple values should work too"
    assert c.id_schema["another_table"] == "my_id2", "Multiple values should work too"


def test_utils_stream_name_to_class_name():
    assert stream_to_class_name("s-a") == "Sa"
    assert stream_to_class_name("s_a") == "S_a"
    assert stream_to_class_name("s _ a") == "S_a"
    assert stream_to_class_name("s{} _ a") == "S_a"
    assert stream_to_class_name("s{} _ aA") == "S_aA"


def test_generate_id():
    assert generate_id("1") == uuid.UUID(int=1)
    assert generate_id("0x1") == uuid.UUID(int=1)
    assert generate_id(1) == uuid.UUID(int=1)
    assert generate_id("123e4567-e89b-12d3-a456-426614174000") == uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
