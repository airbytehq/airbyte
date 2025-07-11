import pytest
import responses
from source_iterable.components import UsersSchemaLoader

@pytest.fixture
def iterable_response_string():
    return {
        "fields": {
            "testString": "string",
        }
    }

@pytest.fixture
def expected_schema_string():
    return {
        "type": ["null", "object"],
        "properties": {
            "testString": {
                "type": [
                    "null",
                    "string"
                ]
            }
        }
    }

@pytest.fixture
def iterable_response_long():
    return {
        "fields": {
            "testLong": "long",
        }
    }

@pytest.fixture
def expected_schema_long():
    return {
        "type": ["null", "object"],
        "properties": {
            "testLong": {
                "type": [
                    "null",
                    "number"
                ]
            }
        }
    }

@pytest.fixture
def iterable_response_double():
    return {
        "fields": {
            "testDouble": "double",
        }
    }

@pytest.fixture
def expected_schema_double():
    return {
        "type": ["null", "object"],
        "properties": {
            "testDouble": {
                "type": [
                    "null",
                    "number"
                ]
            }
        }
    }

@pytest.fixture
def iterable_response_boolean():
    return {
        "fields": {
            "testBoolean": "boolean",
        }
    }

@pytest.fixture
def expected_schema_boolean():
    return {
        "type": ["null", "object"],
        "properties": {
            "testBoolean": {
                "type": [
                    "null",
                    "boolean"
                ]
            }
        }
    }

@pytest.fixture
def iterable_response_date():
    return {
        "fields": {
            "testDate": "date",
        }
    }

@pytest.fixture
def expected_schema_date():
    return {
        "type": ["null", "object"],
        "properties": {
            "testDate": {
                "type": [
                    "null",
                    "string"
                ],
                "format": "date-time"
            }
        }
    }

@pytest.fixture
def iterable_response_geo_location():
    return {
        "fields": {
            "testGeolocation": "geo_location",
        }
    }

@pytest.fixture
def expected_schema_geo_location():
    return {
        "type": ["null", "object"],
        "properties": {
            "testGeolocation": {
                "type": [
                    "null",
                    "object"
                ],
                "properties": {
                    "lat": {
                        "type": [
                            "null",
                            "number"
                        ]
                    },
                    "lon": {
                        "type": [
                            "null",
                            "number"
                        ]
                    }
                }
            }
        }
    }

@pytest.fixture
def iterable_response_object():
    return {
        "fields": {
            "testObject": "object",
            "testObject.testString": "string",
        }
    }

@pytest.fixture
def expected_schema_object():
    return {
        "type": ["null", "object"],
        "properties": {
            "testObject": {
                "type": [
                    "null",
                    "object"
                ],
                "properties": {
                    "testString": {
                        "type": [
                            "null",
                            "string"
                        ]
                    },
                }
            }
        }
    }

@pytest.fixture
def iterable_response_object_and_sub_object():
    return {
        "fields": {
            "testObject": "object",
            "testObject.subObject": "object",
            "testObject.subObject.testString": "string",
        }
    }

@pytest.fixture
def expected_schema_object_and_sub_object():
    return {
        "type": ["null", "object"],
        "properties": {
            "testObject": {
                "type": [
                    "null",
                    "object"
                ],
                "properties": {
                    "subObject": {
                        "type": [
                            "null",
                            "object"
                        ],
                        "properties": {
                            "testString": {
                                "type": [
                                    "null",
                                    "string"
                                ]
                            }
                        }
                    }
                }
            }
        }
    }

@pytest.mark.parametrize("api_response_fixture,expected_schema_fixture", [
    ("iterable_response_string", "expected_schema_string"),
    ("iterable_response_long", "expected_schema_long"),
    ("iterable_response_double", "expected_schema_double"),
    ("iterable_response_boolean", "expected_schema_boolean"),
    ("iterable_response_date", "expected_schema_date"),
    ("iterable_response_geo_location", "expected_schema_geo_location"),
    ("iterable_response_object", "expected_schema_object"),
    ("iterable_response_object_and_sub_object", "expected_schema_object_and_sub_object"),
])
@responses.activate
def test_users_schema_loader_with_data_types(config, api_response_fixture, expected_schema_fixture, request):
    """Test UsersSchemaLoader with various data types."""
    api_response = request.getfixturevalue(api_response_fixture)
    expected_schema = request.getfixturevalue(expected_schema_fixture)

    responses.get(
        "https://api.iterable.com/api/users/getFields",
        json=api_response,
        status=200,
    )

    schema_loader = UsersSchemaLoader(config=config, name="users")

    assert schema_loader.get_json_schema() == expected_schema
