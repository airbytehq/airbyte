import pytest

from source_klarna.schema_applier import SchemaApplier


@pytest.mark.parametrize("instance,schema,expected_result", [
    ({"int": 1},
     {"type": "object", "properties": {"int": {"type": "integer", "hashed": True}}, "$schema": "http://json-schema.org/schema#"},
     {'int': '1a736b2aae78add9ac12e1c6d6e9362ae40dc0eb5927b065f97c733b6437f79db91bc1005d5ec8e917bbfd78f97334a884dbca7b6c5b6c326025c843e3339e21'}),
    ({"obj": {"str": "text", "number": 3.123}},
     {"type": "object", "properties": {"obj": {"type": "object","properties": {"str": {"type": "string", "hashed": True},"number": {"type": "number"}}}},"$schema": "http://json-schema.org/schema#"},
     {'obj': {'str': '83f81c7021958a06070a92de3321dd1d1b16596809d88b486d48690b58fc1b4e5d5a48bd42ef529332e604b70266505cac70c206b2c31e6f39acc6e345b01b06', 'number': 3.123}})
])
def test_hashing(instance, schema, expected_result):
    s = SchemaApplier(b"some_salt", remove_missing=True)
    result = s.apply_schema_transformations(instance, schema)
    assert result == expected_result


@pytest.mark.parametrize("instance,schema", [
    ({"int": 1, "string": "string", "bool": True, "object": {"int": 10}, "empty": {}, "array": [1, 2, 3, 4]},
     {"type": "object", "properties": {"int": {"type": "integer"}, "string": {"type": "string"}, "bool": {"type": "boolean"}, "object": {"type": "object", "properties": {"int": {"type": "integer"}}}, "empty": {"type": "object", "properties": {}}, "array": {"type": "array", "items": {"type": "integer"}}},"$schema": "http://json-schema.org/schema#"}),
])
def test_walking(instance, schema):
    # ["1", "13", {"tax_rate": 1, "tax_amount": 5}]
    s = SchemaApplier(b"", remove_missing=True)
    result = s.apply_schema_transformations(instance, schema)
    assert result == instance


@pytest.mark.parametrize("instance,schema,expected_result", [
    ({"int": 1},
     {"type": "object", "properties": {"int": {"type": "integer", "empty": True}}, "$schema": "http://json-schema.org/schema#"},
     {'int': ''}),
    ({"obj": {"str": "text", "number": 3.123}},
     {"type": "object", "properties": {"obj": {"type": "object", "properties": {"str": {"type": "string", "empty": True},"number": {"type": "number"}}}},"$schema": "http://json-schema.org/schema#"},
     {'obj': {'str': '', 'number': 3.123}})
])
def test_emptying(instance, schema, expected_result):
    s = SchemaApplier(b"", remove_missing=True)
    result = s.apply_schema_transformations(instance, schema)
    assert result == expected_result

@pytest.mark.parametrize("instance,schema,expected_result", [
    ({"int": 1},
     {"type": "object", "properties": {"int": {"type": "integer", "empty": True, "hashed": True}}, "$schema": "http://json-schema.org/schema#"},
     {'int': ''}),
    ({"obj": {"str": "text", "number": 3.123}},
     {"type": "object", "properties": {"obj": {"type": "object","properties": {"str": {"type": "string", "empty": True, "hashed": True}, "number": {"type": "number"}}}},"$schema": "http://json-schema.org/schema#"},
     {'obj': {'str': '', 'number': 3.123}}),
    ([{"a": 1, "b": 2}, {"a": 1, "b": 2}, {"a": 1, "b": 2}],
     {"type": "array", "items": {"type": "object", 'properties': {"a": {"type": "integer", "empty": True}, "b": {"type": "integer", "hashed": True}}}, "$schema": "http://json-schema.org/schema#"},
     [{"a": "", "b": "564e1971233e098c26d412f2d4e652742355e616fed8ba88fc9750f869aac1c29cb944175c374a7b6769989aa7a4216198ee12f53bf7827850dfe28540587a97"}, {"a": "", "b": "564e1971233e098c26d412f2d4e652742355e616fed8ba88fc9750f869aac1c29cb944175c374a7b6769989aa7a4216198ee12f53bf7827850dfe28540587a97"}, {"a": "", "b": "564e1971233e098c26d412f2d4e652742355e616fed8ba88fc9750f869aac1c29cb944175c374a7b6769989aa7a4216198ee12f53bf7827850dfe28540587a97"}])
])
def test_emptying_and_hashing(instance, schema, expected_result):
    s = SchemaApplier(b"", remove_missing=True)
    result = s.apply_schema_transformations(instance, schema)
    assert result == expected_result

@pytest.mark.parametrize("instance,schema,expected_result", [
    ({"int": 1},
     {"type": "object", "$schema": "http://json-schema.org/schema#"},
     {}),
    ({"obj": {"str": "text", "number": 3.123}},
     {"type": "object", "properties": {"obj": {"type": "object","properties": {"number": {"type": "number"}}}},"$schema": "http://json-schema.org/schema#"},
     {'obj': {'number': 3.123}}),
    ({"obj": {"str": "text", "number": 3.123}},
     {"type": "object", "properties": {},"$schema": "http://json-schema.org/schema#"},
     {}),
    ({"array": [1,2,3,4,5], 'number': 3.123},
     {"type": "object", "properties": {"array": {"type": "array", "items": {"type": "integer"}}},"$schema": "http://json-schema.org/schema#"},
     {"array": [1,2,3,4,5]}),
    ({"array": [1,2,3,4,5], 'number': 3.123},
     {"type": "object", "properties": {"array": {"type": "array"}},"$schema": "http://json-schema.org/schema#"},
     {'array': []}),
    ({"array": [1,2,3,4,5], 'number': 3.123},
     {"type": "object", "$schema": "http://json-schema.org/schema#"},
     {}),
    ([{"a": 1, "b": 2},  {"a": 1, "b": 2}, {"a": 1, "b": 2}],
     {"type": "array", "items": {"type": "object", 'properties': {}}, "$schema": "http://json-schema.org/schema#"},
     [{}, {}, {}]),
    ([{"a": 1, "b": 2},  {"a": 1, "b": 2}, {"a": 1, "b": 2}],
     {"type": "array", "items": {}, "$schema": "http://json-schema.org/schema#"},
     []),
    ([{"a": 1, "b": 2},  {"a": 1, "b": 2}, {"a": 1, "b": 2}],
     {"type": "array", "$schema": "http://json-schema.org/schema#"},
     []),
    ([{"a": 1, "b": 2}, {"a": 1, "b": 2}, {"a": 1, "b": 2}],
     {"type": "array", "items": {"type": "object", 'properties': {"a": {"type": "integer"}}}, "$schema": "http://json-schema.org/schema#"},
     [{"a": 1}, {"a": 1}, {"a": 1}])
])
def test_remove_missing(instance, schema, expected_result):
    s = SchemaApplier(b"", remove_missing=True)
    result = s.apply_schema_transformations(instance, schema)
    assert result == expected_result