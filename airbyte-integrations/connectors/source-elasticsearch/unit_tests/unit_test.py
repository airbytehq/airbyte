#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import pytest

from source_elasticsearch.source import SourceElasticsearch, UnsupportedDataTypeException


def test_get_indices(mocker):
    mocked_es = mocker.MagicMock()
    mocked_es.indices.get.return_value = {
        ".kibana_1": "foo",
        "other_index": "bar",
    }
    assert SourceElasticsearch()._get_indices(mocked_es) == {
        "other_index": "bar"
    }


def test_get_index_json_properties_happy_path(mocker):
    mocked_es = mocker.MagicMock()
    mocked_es.indices.get_mapping.return_value = {
        "index_name": {
            "mappings": {
                "properties": {
                    "text_property": {
                        "type": "text"
                    },
                    "integer_property": {
                        "type": "integer"
                    },
                    "float_property": {
                        "type": "float"
                    },
                    "date_property": {
                        "type": "date"
                    },
                }
            }
        }
    }
    assert SourceElasticsearch()._get_index_json_properties(mocked_es, "index_name") == {
        "text_property": {
            "type": "string"
        },
        "integer_property": {
            "type": "integer"
        },
        "float_property": {
            "type": "number"
        },
        "date_property": {
            "type": "string"
        },
    }


def test_get_index_json_properties_unsupported_tyoe(mocker):
    mocked_es = mocker.MagicMock()
    mocked_es.indices.get_mapping.return_value = {
        "index_name": {
            "mappings": {
                "properties": {
                    "unsupported_property": {
                        "type": "unsupported"
                    },
                }
            }
        }
    }
    with pytest.raises(UnsupportedDataTypeException):
        SourceElasticsearch()._get_index_json_properties(mocked_es, "index_name")
